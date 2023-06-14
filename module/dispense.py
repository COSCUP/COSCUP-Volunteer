''' Dispense '''
from typing import Any, Generator

from pymongo.collection import ReturnDocument
from pymongo.cursor import Cursor

from models.expensedb import ExpenseDB
from models.dispensedb import DispenseDB
from models.budgetdb import BudgetDB

from module.expense import Expense

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
    def get_order_by_date(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all and sort by dispense_date and create_at

        Args:
            pid (str): Project id.

        Yields:
            Return the dispense data in `pid`
        '''
        for raw in DispenseDB().find({'pid': pid}).sort([
                ('dispense_date', 1),
                ('create_at', 1)]):
            yield raw

    @staticmethod
    def get_by_ids(ids: list[str]) -> Cursor[dict[str, Any]]:
        ''' Get all

        Args:
            ids (list[str]): list of dispense id.

        Returns:
            Return the dispense data in `ids`.

        '''
        return DispenseDB().find({'_id': { '$in': ids }})

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
        for allowed_key in ('status', 'dispense_date', 'enable'):
            if allowed_key in data:
                to_set[allowed_key] = data[allowed_key]

        if 'enable' in to_set and to_set['enable']:
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

    @staticmethod
    def dl_format(pid: str) -> list[dict[str, Any]]:
        ''' Make the dispense format

        The fields datas:

            - `出款日期`: `dispense.dispense_date`
            - `出款總金額` `Sum of expense.incoice.total`
            - `組別`: `expense.tid`.
            - `申請單狀態`: `expense.enable`.
            - `編號`: `budget.bid`.
            - `預算項目`: `budget.name`.
            - `預算貨幣`: `budget.currency`.
            - `預算金額`: `budget.total`.
            - `會計科目`: ` `.
            - `請款狀態`: `ExpenseDB.status()[expense['status']]`.
            - `申請時間`: `expense.create_at`.
            - `分行名稱`: `expense.bank.branch`.
            - `分行代碼`: `expense.bank.code`.
            - `帳戶名稱`: `expense.bank.name`.
            - `帳號`: `expense.bank.no`.
            - `單據名稱`: `expense.invoice.name`.
            - `單據貨幣`: `expense.invoice.currency`.
            - `單據金額`: `expense.invoice.total`.
            - `單據是否收到`: `expense.invoice.received`.
        '''
        raws = []

        for dispense in Dispense.get_order_by_date(pid):
            if dispense['enable'] is False:
                continue

            expenses = Expense.get_by_dispense_id([dispense['_id']])
            expense_raws = []

            dispense_base = {
                '出款日期': dispense['dispense_date'],
                '出款總金額': 0,
                '組別': '',
                '申請單狀態': '',
                '編號': '',
                '預算項目': '',
                '預算貨幣': '',
                '預算金額': '',
                '會計科目': '',
                '請款狀態': '',
                '申請時間': '',
                '分行名稱': '',
                '分行代碼': '',
                '帳戶名稱': '',
                '帳號': '',
                '單據名稱': '',
                '單據貨幣': '',
                '單據金額': '',
                '單據是否收到': '',
            }

            for expense in expenses:
                if expense['enable'] is False:
                    continue

                expense_base = {
                    '組別': expense['tid'],
                    '申請單狀態': expense['enable'],
                    '編號': '',
                    '預算項目': '',
                    '預算貨幣': '',
                    '預算金額': '',
                    '會計科目': '',
                    '請款狀態': ExpenseDB.status()[expense['status']],
                    '申請時間': expense['create_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    '分行名稱': expense['bank']['branch'],
                    '分行代碼': expense['bank']['code'],
                    '帳戶名稱': expense['bank']['name'],
                    '帳號': expense['bank']['no'],
                }

                for budget in BudgetDB().find({'_id': expense['request']['buid']}):
                    expense_base['編號'] = budget['bid']
                    expense_base['預算項目'] = budget['name']
                    expense_base['預算貨幣'] = budget['currency']
                    expense_base['預算金額'] = budget['total']

                for invoice in expense['invoices']:
                    data = {}
                    data.update(expense_base)

                    dispense_base['出款總金額'] += invoice['total']
                    invoice_data = {
                        '單據名稱': invoice['name'],
                        '單據貨幣': invoice['currency'],
                        '單據金額': invoice['total'],
                        '單據是否收到': invoice['received'],
                    }

                    data.update(invoice_data)
                    expense_raws.append(data)

            raws.append(dispense_base)
            raws.extend(expense_raws)

        return raws
