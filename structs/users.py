''' User Structs '''
from enum import Enum
from datetime import datetime
from time import time
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from module.dietary_habit import DietaryHabitItemsValue


class UserProfle(BaseModel):
    ''' User Profile struct

    Attributes:
        badge_name: Badge name.
        intro: introduction.

    '''
    badge_name: str = Field(default='', example='Badge Name')
    intro: str = Field(default='', description='Markdown format')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


class UserBank(BaseModel):
    ''' User Bank info

    Attributes:
        code: bank code.
        no: bank account numbers.
        branch: bank branch name.
        name: bank account name.

    '''
    code: str = Field(default='', description='bank code')
    no: str = Field(default='', description='bank account numbers')
    branch: str = Field(default='', description='bank branch name')
    name: str = Field(default='', description='bank account name')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


class UserAddress(BaseModel):
    ''' User Address

    Attributes:
        code: postal code.
        receiver: receiver name.
        address: address.

    '''
    code: str = Field(default='')
    receiver: str = Field(default='')
    address: str = Field(default='')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


class UserProfleRealBase(BaseModel):
    ''' User Profile Real Base struct

    Attributes:
        name: name.
        phone: phone numbers.
        roc_id: user national id.
        company: company or school name.

    '''
    name: str = Field(default='')
    phone: str = Field(default='')
    roc_id: str = Field(default='')
    company: str = Field(default='')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


class UserProfleReal(UserProfleRealBase):
    ''' User Profile Real struct

    Attributes:
        birthday: *(optional)* birthday.
        bank: *(optional)* bank info.
        address: *(optional)* address info.
        dietary_habit: *(optional)* dietary habit info.

    '''
    birthday: Optional[datetime] = Field(default=None)
    bank: Optional[UserBank] = Field(default_factory=UserBank)
    address: Optional[UserAddress] = Field(default_factory=UserAddress)
    dietary_habit: Optional[list[DietaryHabitItemsValue]] = Field(
        default_factory=list)

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`
            use_enum_values: `True`

        '''
        anystr_strip_whitespace: bool = True
        use_enum_values: bool = True


class User(BaseModel):
    ''' User struct

    Attributes:
        id: user id. *(alias: `_id`)*
        created_at: timestamp.
        mail: mail.
        profile: profile info.
        profile_real: real profile info.

    !!! TODO

        Need to convert the `int` type to `datetime` of `created_at`.

    '''
    id: str = Field(..., alias='_id')
    created_at: int = Field(default_factory=lambda: int(time()))
    mail: EmailStr = Field(..., description="User's mail")
    profile: Optional[UserProfle]
    profile_real: Optional[UserProfleReal]

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


class PolicyType(str, Enum):
    ''' Policy Type '''
    COC = 'coc'
    SECURITY_GUARD = 'security_guard'


class PolicySigned(BaseModel):
    ''' Policy Signed struct

    Attributes:
        uid: user id.
        type: type of [PolicyType](PolicyType).
        sign_at: datetime.

    '''
    uid: str = Field(description='user id')
    type: PolicyType = Field(description='Policy type')
    sign_at: datetime = Field(
        description='The policy signed at', default_factory=datetime.now)

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config'''
        use_enum_values = True
