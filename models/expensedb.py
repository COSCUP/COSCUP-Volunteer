''' ExpenseDB '''
import string
from datetime import datetime
from random import choices
from typing import Any
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class ExpenseDB(DBBase):
    ''' Expense Collection '''

    def __init__(self) -> None:
        super().__init__('expense')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`, `tid`
            - `pid`, `tid`, `request.buid`
            - `pid`, `tid`, `create_by`

        '''
        self.create_index([('pid', 1), ('tid', 1)])
        self.create_index([('pid', 1), ('tid', 1), ('request.buid', 1)])
        self.create_index([('pid', 1), ('tid', 1), ('create_by', 1)])

    @staticmethod
    def status() -> dict[str, str]:
        ''' Status mapping

        Returns:
            `1`: `已申請`, `2`: `審核中`, `3`: `出款中`, `4`: `已出款`, `5`: `已完成`

        '''
        return {'1': '已申請',
                '2': '審核中',
                '3': '出款中',
                '4': '已出款',
                '5': '已完成',
                }

    @staticmethod
    def new(pid: str, tid: str, uid: str) -> dict[str, Any]:
        ''' Create new data object

        Args:
            pid (str): project id
            tid (str): team id
            uid (str): user id

        Struct:
            - ``_id``: Unique expense id.
            - ``pid``: Project id.
            - ``tid``: Team id.
            - ``dispense_id``: Reference to expense DB, if any
            - ``request``: This object include the budget data in
                           `buid`, `desc`, `paydate`, `code`.
            - ``invoices``: List of invoice data, in `iv_id`,
                            `currency`, `name`, `status`, `total`, `received`.
            - ``bank``: User's bank account info, the data from user's
                        real_profile in settings.
            - ``status``: The mappings from [`ExpenseDB.status`][models.expensedb.ExpenseDB.status].
            - ``note``: Note fields, but not implememnt in expense page.
            - ``code``: Random shorter code for reference in batch.
            - ``releveant_code``: The codes are releveant to others.
            - ``create_by``: Create by who in `uid`.
            - ``create_at``: When to created.
            - ``enable`` (`bool`): enable or not.

        Returns:
            Return an base data object in `dict`.

        TODO:
            Need refactor in pydantic.

        '''
        return {
            '_id': f'{uuid4().node:x}',
            'pid': pid,
            'tid': tid,
            'dispense_id': '',
            'request': {},
            'invoices': [],
            'bank': {},
            'status': '1',  # 已申請/處理中/已出款/已完成
            'note': {'myself': '', 'to_create': ''},
            'code': f"E-{''.join(choices(string.ascii_uppercase+string.digits, k=4))}",
            'relevant_code': [],
            'create_by': uid,
            'create_at': datetime.today(),
            'enable': True,
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
