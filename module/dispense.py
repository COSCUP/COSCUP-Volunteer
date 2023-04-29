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
    def update_dispense_date(dispense_id: str, dispense_date: datetime) -> dict[str, Any]:
        '''
        Only update dispense_date

        Args:
            dispense_id (str): _id in DispenseDB
            dispense_date (datetime): date of dispense

        Returns:
            Return the updated data
        '''
        return DispenseDB().find_one_and_update(
            {'_id': dispense_id},
            {'$set': {'dispense_date': dispense_date}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_status(dispense_id: str, status: str) -> dict[str, Any]:
        ''' update status

        Args:
            dispense_id (str): The dispense id is the unique `_id`.
            status (str): The key in [module.expense.Expense.status][].

        Returns:
            Return the updated data.

        '''
        return DispenseDB().find_one_and_update(
            {'_id': dispense_id},
            {'$set': {'status': status.strip()}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_enable(dispense_id: str, enable: bool) -> dict[str, Any]:
        ''' update enable

        Args:
            expense_id (str): The expense id is the unique `_id`.
            enable (bool): update the enable.

        Returns:
            Return the updated data.

        '''
        return DispenseDB().find_one_and_update(
            {'_id': dispense_id},
            {'$set': {'enable': bool(enable)}},
            return_document=ReturnDocument.AFTER,
        )
