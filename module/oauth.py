''' OAuth '''
from typing import Any, Optional

from google.oauth2.credentials import Credentials  # type: ignore

from models.oauth_db import OAuthDB


class OAuth:
    ''' OAuth

    Args:
        mail (str): Mail address

    '''

    def __init__(self, mail: str) -> None:
        self.mail = mail

    def get(self) -> Optional[dict[str, Any]]:
        ''' Get data

        Returns:
            Return the data by the mail.

        '''
        return OAuthDB().find_one({'_id': self.mail})

    @staticmethod
    def add(mail: str, data: Optional[dict[str, Any]] = None,
            token: Optional[Credentials] = None) -> None:
        ''' add data, token

        Args:
            mail (str): Mail address.
            data (dict): The data from the oauth response.
            token (dict): OAuth token.

        '''

        if any((data, token)):
            oauth_db = OAuthDB()

            if data is not None:
                oauth_db.add_data(mail=mail, data=data)

            if token is not None:
                oauth_db.add_token(mail=mail, credentials=token)

    @staticmethod
    def owner(mail: str) -> Optional[str]:
        ''' return the owner

        Args:
            mail (str): Mail address.

        Raises:
            Exception: No oauth data of `{mail}`.

        '''
        data = OAuthDB().find_one({'_id': mail}, {'owner': 1})
        if not data:
            raise Exception(f'No oauth data of `{mail}`')

        return data.get('owner')
