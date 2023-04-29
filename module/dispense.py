''' Dispense '''
from typing import Any, Generator
from datetime import datetime

from pymongo.collection import ReturnDocument

from models.expensedb import ExpenseDB
from models.dispensedb import DispenseDB

class Dispense:
    ''' Dispense class '''

    @staticmethod
    def create(pid: str, expense_ids: list[str], dispense_date: str) -> dict[str, Any]:
        '''
        Create dispense and correlate to ExpenseDB

        Args:
            pid (str): Project id
            expense_ids (list[str]): List of expense collection id in this
                dispense, readonly once created

        Returns:
            The created dispense object
        '''
        dispense_data = DispenseDB.new(pid, expense_ids)
        dispense_data['dispense_date'] = dispense_date
        dispense = DispenseDB().add(data = dispense_data)

        for expense_id in expense_ids:
            ExpenseDB().find_one_and_update(
                { '_id': expense_id },
                {
                    '$set': {
                        'dispense_id': dispense['_id'],
                        'status': '3' # 出款中
                    }
                },
                return_document=ReturnDocument.AFTER,
            )

        return dispense

    @staticmethod
    def status() -> dict[str, str]:
        ''' Get status

        Returns:
            Return the status mapping from [models.expensedb.ExpenseDB.status][]

        '''
        return ExpenseDB.status()

    @staticmethod
    def get_all_by_pid(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all

        Args:
            pid (str): Project id.

        Yields:
            Return the dispense data in `pid`.

        '''
        for raw in DispenseDB().find({'pid': pid}):
            yield raw

    @staticmethod
    def update(dispense_id: str, data: dict[str, Any]) -> dict[str, Any] | int:
        '''
        Only update dispense_date

        Args:
            dispense_id (str): _id in DispenseDB
            data (dict[str, Any]): data to be applied, only status, enable,
                and dispense_date are writable

        Returns:
            Return the updated data
        '''
        to_set = {}
        for allowed_key in ['status', 'dispense_date', 'enable']:
            if allowed_key in data:
                to_set[allowed_key] = data[allowed_key]

        if to_set['enable']:
            return 403

        resp = DispenseDB().find_one_and_update(
            {'_id': dispense_id},
            {'$set': to_set},
            return_document=ReturnDocument.AFTER,
        )

        if 'enable' in to_set and not to_set['enable']:
            # restore expense
            for exp_id in resp['expense_ids']:
                ExpenseDB().find_one_and_update(
                    {'_id': exp_id},
                    {'$set': {'status': '2'}}, # back to 審核中
                    return_document=ReturnDocument.AFTER,
                )

        return resp
