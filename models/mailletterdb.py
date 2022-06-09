''' MailLetterDB

This models will save the record of what the platform send the specific case of mail to user.
(like: `welcome` letter)

The base struct::

    {
        "_id" : <user id>,
        "create_at" : <timestamp>,
        "code" : {
            "welcome" : <timestamp>
        }
    }

'''
from time import time
from typing import Any, Generator

from pymongo.collection import ReturnDocument

from models.base import DBBase


class MailLetterDB(DBBase):
    ''' MailLetterDB Collection '''

    def __init__(self) -> None:
        super().__init__('mailletter')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `code.welcome`

        '''
        self.create_index([('code.welcome', 1), ])

    def create(self, uid: str) -> None:
        ''' Add user into sendlist

        Args:
            uid (str): User id.

        '''
        self.find_one_and_update(
            {'_id': uid}, {'$set': {'create_at': time()}}, upsert=True)

    def is_sent(self, uid: str, code: str) -> float:
        ''' Check is sent or not

        Args:
            uid (str): User id.
            code (str): case code.

        Returns:
            The `timestamp` value. `0` has not sent.

        '''
        raw = self.find_one({'_id': uid}, {f'code.{code}': 1})
        if raw and 'code' in raw and code in raw['code']:
            return float(raw['code'][code])

        return 0

    def make_sent(self, uid: str, code: str) -> dict[str, Any]:
        ''' Make sent record

        Args:
            uid (str): User id.
            code (str): Case code.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': uid},
            {'$set': {f'code.{code}': time()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def need_to_send(self, code: str) -> Generator[dict[str, Any], None, None]:
        ''' Find need to send the list of user

        Args:
            code (str): Case code.

        Yields:
            The data haven't been sent yet.

        '''
        for raw in self.find({f'code.{code}': {'$exists': False}}):
            yield raw
