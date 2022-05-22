''' oauth database '''
from typing import Any

import google_auth_oauthlib.flow  # type: ignore

from models.base import DBBase


class OAuthDB(DBBase):  # pylint: disable=abstract-method
    ''' OAuthDB Collection '''

    def __init__(self) -> None:
        super().__init__('oauth')

    def index(self) -> None:
        ''' Index '''
        self.create_index([('owner', 1), ])

    def add_data(self, mail: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add user data

        :param str mail: email
        :param dict data: user data

        '''
        return self.find_one_and_update(
            {'_id': mail},
            {'$set': {'data': data}},
            upsert=True)

    def add_token(self, mail: str, credentials: google_auth_oauthlib.flow) -> None:
        ''' Add user oauth token

        :param str mail: email
        :param dict credentials: user oauth token, from ``flow.credentials``

        .. note:: Not to save ``client_id``, ``client_secret``

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
        ''' Setup owner

        :param str mail: mail
        :param str uid: uid

        '''
        self.find_one_and_update({'_id': mail}, {'$set': {'owner': uid}})
