''' oauth database '''
from typing import Any

from google.oauth2.credentials import Credentials  # type: ignore

from models.base import DBBase


class OAuthDB(DBBase):  # pylint: disable=abstract-method
    ''' OAuthDB Collection '''

    def __init__(self) -> None:
        super().__init__('oauth')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `owner`

        '''
        self.create_index([('owner', 1), ])

    def add_data(self, mail: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add user data

        Args:
            mail (str): Email address as unique key to save.
            data (dict): The data from Google OAuth return.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': mail},
            {'$set': {'data': data}},
            upsert=True)

    def add_token(self, mail: str, credentials: Credentials) -> None:
        ''' Add user oauth token

        Args:
            mail (str): Email address.
            credentials: [google.oauth2.credentials.Credentials][]

        '''
        oauth = self.find_one({'_id': mail}, {'token': 1})
        if oauth and 'token' in oauth:
            data = oauth['token']
        else:
            data = {}

        data['token'] = credentials.token
        if credentials.refresh_token:
            data['refresh_token'] = credentials.refresh_token

        data['token_uri'] = credentials.token_uri
        data['id_token'] = credentials.id_token
        data['scopes'] = credentials.scopes

        self.find_one_and_update(
            {'_id': mail},
            {'$set': {'token': data}},
            upsert=True)

    def setup_owner(self, mail: str, uid: str) -> None:
        ''' Setup user id into `owner` field

        Args:
            mail (str): Email address.
            uid (str): User id.

        '''
        self.find_one_and_update({'_id': mail}, {'$set': {'owner': uid}})
