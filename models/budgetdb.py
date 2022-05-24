''' BudgetDB '''
import string
from datetime import datetime
from random import choices
from typing import Any
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class BudgetDB(DBBase):
    ''' Budget Collection

    :Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``bid``: budget id
        - ``name``: team name
        - ``uid``: user id
        - ``currency``: TWD, USD
        - ``total``: 0.00
        - ``paydate``: ISO8601
        - ``desc``: desc
        - ``estimate``: estimate
        - ``create_at``: create date

    '''

    def __init__(self) -> None:
        super().__init__('budget')

    def index(self) -> None:
        ''' Index '''
        self.create_index([('pid', 1), ('tid', 1)])
        self.create_index([('pid', 1), ('bid', 1)])

    @staticmethod
    def new(pid: str, tid: str, uid: str) -> dict[str, Any]:
        ''' Create new '''
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
        ''' Add data

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'pid': data['pid'], 'tid': data['tid'], '_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def edit(self, _id: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Edit data

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'_id': _id},
            {'$set': data},
            return_document=ReturnDocument.AFTER,
        )
