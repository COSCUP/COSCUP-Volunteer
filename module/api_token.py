''' Module API Token '''
from datetime import datetime
from enum import Enum
from uuid import uuid4

import arrow
from passlib.context import CryptContext  # type: ignore
from pydantic import BaseModel, Field

from models.api_tokendb import APITokenDB


class APITokenType(str, Enum):
    ''' APITokenType '''
    TEMP = 'temp'
    SESSION = 'session'


class APITokenBase(BaseModel):
    ''' APITokenBase '''
    uid: str
    create_at: datetime = Field(default_factory=datetime.now)
    alive: bool = Field(default=True)
    token_type: APITokenType

    class Config:  # pylint: disable=too-few-public-methods
        ''' config '''
        use_enum_values = True


class APITokenTemp(APITokenBase):
    ''' API Temp Token '''
    token_type: APITokenType = Field(default=APITokenType.TEMP)
    username: str = Field(description='login username',
                          default_factory=lambda: uuid4().hex)
    password: str = Field(description='login password',
                          default_factory=lambda: f'{uuid4().node:08x}'[:6])


class APITokenSession(APITokenBase):
    ''' API Session Token '''
    token_type: APITokenType = Field(default=APITokenType.SESSION)
    token: str = Field(default_factory=lambda: uuid4().hex)
    serial_no: str = Field(default_factory=lambda: f'{uuid4().node:08x}')


class APIToken:  # pylint: disable=too-few-public-methods
    ''' API Token '''
    @staticmethod
    def save_temp(data: APITokenTemp) -> None:
        ''' Save temp token '''
        hash_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        save_data = data.dict()
        save_data['password'] = hash_context.hash(data.password)
        APITokenDB().insert_one(save_data)

    @staticmethod
    def verify(username: str, password: str) -> str | None:
        ''' Verify the username and password

        Args:
            username (str): username
            password (str): password

        Return: str | None

        '''
        row: dict[str, str]
        for row in APITokenDB().find({
                'token_type': 'temp',
                'alive': True,
                'username': username,
                'create_at': {'$gte': arrow.now().shift(minutes=-5).naive},
        }):
            hash_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
            if hash_context.verify(password, row['password']):
                APITokenDB().update_one(
                    {'token_type': 'temp', 'alive': True, 'username': username},
                    {'$set': {'alive': False}},
                )
                return row['uid']

        return None

    @staticmethod
    def create_token(uid: str) -> str:
        ''' Create access token

        Args:
            uid (str): uid

        Return: token

        '''
        token = APITokenSession(uid=uid)

        save_data = token.dict()
        hash_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        save_data['token'] = hash_context.hash(token.token)
        APITokenDB().insert_one(save_data)

        return f'{token.serial_no}|{token.token}'

    @staticmethod
    def verify_token(token: str) -> str | None:
        ''' verify the token

        Args:
            token (str): token

        Return: str | None

        '''
        serial_no, plain_token = token.split('|')

        row: dict[str, str]
        for row in APITokenDB().find({
                'token_type': 'session',
                'alive': True,
                'serial_no': serial_no,
        }):
            hash_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
            if hash_context.verify(plain_token, row['token']):
                return row['uid']

        return None
