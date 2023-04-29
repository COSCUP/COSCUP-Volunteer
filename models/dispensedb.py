''' DispenseDB '''
from datetime import datetime
from typing import Any
from uuid import uuid4
from pymongo.collection import ReturnDocument

from models.base import DBBase


class DispenseDB(DBBase):
    '''
    Dispense Collection

    This collection aggregate expense record into a single payment record.
    出款單是用來紀錄「單筆匯款」裡有哪些「請款單」的資料格式
    '''

    def __init__(self) -> None:
        super().__init__('dispense')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`
        '''
        self.create_index([('pid', 1)])

    @staticmethod
    def new(pid: str, expense_ids: list[str]) -> dict[str, Any]:
        ''' Create new data object

        Args:
            pid (str): project id
            expense_ids: list[str]: array of expense id

        Struct:
            - ``_id``: Unique dispense id.
            - ``pid``: Project id.
            - ``expense_ids``: List of expense id.
            - ``status``: The mappings from [`ExpenseDB.status`][models.expensedb.ExpenseDB.status].
            - ``create_at``: When to create.
            - ``dispense_date``: Estimate date to dispense.
            - ``enable`` (`bool`): enable or not.

        Returns:
            Return an base data object in `dict`.
        '''

        return {
            '_id': f'{uuid4().node:x}',
            'pid': pid,
            'expense_ids': expense_ids,
            'status': '3', # 出款中
            'create_at': datetime.today(),
            'dispense_date': '',
            'enable': True,
        }


    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add data, using `_id` as the key to insert / update.

        Args:
            data (dict): the data to insert / update.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
