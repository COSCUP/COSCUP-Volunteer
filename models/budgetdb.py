''' BudgetDB '''
import string
from datetime import datetime
from random import choices
from typing import Any
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class BudgetDB(DBBase):
    ''' Budget Collection '''

    def __init__(self) -> None:
        super().__init__('budget')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`, `tid`
            - `pid`, `bid`

        '''
        self.create_index([('pid', 1), ('tid', 1)])
        self.create_index([('pid', 1), ('bid', 1)])

    @staticmethod
    def new(pid: str, tid: str, uid: str) -> dict[str, Any]:
        ''' Create new

        Struct:

            - ``_id``: Unique budget id.
            - ``pid``: Project id.
            - ``tid``: Team id.
            - ``bid``: This buDget id is from the google spreadsheet
                       by serials in manually.
            - ``name``: Team name.
            - ``uid``: User id.
            - ``currency``: Now only support in `TWD`, `USD`.
            - ``total``: 0.00
            - ``paydate``: `str` In ISO8601 format or `YYYY-MM-DD`.
            - ``desc``: Descrption.
            - ``estimate``: more descriptions in how to estimate the total.
            - ``code``: Random shorter code for reference in batch.
            - ``enabled``: `bool`.
            - ``create_at``: The created date.

        Args:
            pid (str): project id
            tid (str): team id
            uid (str): user id

        Returns:
            Return an base data object in `dict`.

        TODO:
            Need refactor in pydantic.

        '''
        return {
            '_id': f'{uuid4().node:x}',
            'pid': pid,
            'tid': tid,
            'bid': '',
            'name': '',
            'uid': uid,
            'currency': 'TWD',
            'total': 0,
            'paydate': '',
            'desc': '',
            'estimate': '',
            'code': f"B-{''.join(choices(string.ascii_uppercase+string.digits, k=4))}",
            'enabled': True,
            'create_at': datetime.today(),
        }

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add data, using `pid`, `tid`, `_id` as the key to insert / update.

        Args:
            data (dict): the data to insert / update.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'pid': data['pid'], 'tid': data['tid'], '_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def edit(self, _id: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Edit data, using the `_id` as the key.

        Args:
            _id (str): the budget id.
            data (dict): the data need to update.

        Returns:
            Return the updated data.

        '''
        return self.find_one_and_update(
            {'_id': _id},
            {'$set': data},
            return_document=ReturnDocument.AFTER,
        )
