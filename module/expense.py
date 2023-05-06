''' Expense '''
import string
from random import choices
from typing import Any, Generator

from pymongo.collection import ReturnDocument
from pymongo.cursor import Cursor

from models.budgetdb import BudgetDB
from models.expensedb import ExpenseDB

class Expense:
    ''' Expense class '''

    @staticmethod
    def process_and_add(pid: str, tid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Process data from web

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.
            data (dict): The data from user to submit the expense requests.
                These fields are required:

                - `expense_request`
                    - `buid`: Budget id.
                    - `desc`: Description.
                    - `paydate`: The pay date.
                    - `code`: Short code.
                    - `relevant`: Relevant budget id.
                - `bank`:
                    - `branch`: Bank branch.
                    - `code`: Bank code.
                    - `name`: Account name.
                    - `no`: Account no.
                - `invoices`: (List of data).
                    - `iv_id`: Invoice id
                    - `currency`: List of the values in [module.budget.Currency][]
                    - `name`: Invoice name.
                    - `status`: Invoice status. (`not_send`, `sent`, `no_invoice`)
                    - `total`: Invoice total.
                    - `received`: (bool) is received or not.

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        save = ExpenseDB.new(pid=pid, tid=tid, uid=uid)

        save['request'] = {
            'buid': data['expense_request']['buid'],
            'desc': data['expense_request']['desc'],
            'paydate': data['expense_request']['paydate'],
            'code': data['expense_request']['code'],
        }

        # check the relevant expense codes
        for expense in ExpenseDB().find({'pid': pid,
                                         'code': {
                                             '$in': list(filter(
                                                 lambda x: x,
                                                 data['expense_request']['relevant']))}}):
            save['relevant_code'].append(expense['code'])

        save['bank'] = {
            'branch': data['bank']['branch'],
            'code': data['bank']['code'],
            'name': data['bank']['name'],
            'no': data['bank']['no'],
        }

        for invoice in data['invoices']:
            if invoice['status'] not in ('', 'not_send', 'sent', 'no_invoice'):
                continue

            save['invoices'].append(
                {
                    'iv_id': f"IV-{''.join(choices(string.ascii_uppercase+string.digits, k=4))}",
                    'currency': invoice['currency'],
                    'name': invoice['name'],
                    'status': invoice['status'],
                    'total': invoice['total'],
                    'received': False,
                })

        return ExpenseDB().add(data=save)

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
            Return the expenses data in `pid`.

        '''
        for raw in ExpenseDB().find({'pid': pid}):
            yield raw

    @staticmethod
    def get_by_eid(expense_id: str) -> Generator[dict[str, Any], None, None]:
        ''' Get one expense data

        Args:
            expense_id (str): Expense id.

        Yields:
            Return the expenses data in `expense_id`.

        '''
        for raw in ExpenseDB().find({'_id': expense_id}):
            yield raw

    @staticmethod
    def update_invoices(expense_id: str, invoices: list[dict[str, Any]]) -> dict[str, Any]:
        ''' Only update invoices

        Args:
            expense_id (str): The expense id is the unique `_id`.
            invoices (list): List of invoice datas.
                These fields are required:

                - `iv_id`: Invoice id
                - `currency`: List of the values in [module.budget.Currency][]
                - `name`: Invoice name.
                - `status`: Invoice status. (`not_send`, `sent`, `no_invoice`)
                - `total`: Invoice total.
                - `received`: (bool) is received or not.

        Returns:
            Return the updated data.

        TODO:
            Need refactor in pydantic.

        '''
        _invoices = []
        for invoice in invoices:
            _invoices.append(
                {'iv_id': invoice['iv_id'].strip(),
                 'currency': invoice['currency'].strip(),
                 'name': invoice['name'].strip(),
                 'status': invoice['status'].strip(),
                 'total': invoice['total'],
                 'received': invoice['received'] if 'received' in invoice else False,
                 })

        return ExpenseDB().find_one_and_update(
            {'_id': expense_id},
            {'$set': {'invoices': _invoices}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_status(expense_id: str, status: str) -> dict[str, Any]:
        ''' update status

        Args:
            expense_id (str): The expense id is the unique `_id`.
            status (str): The key in [module.expense.Expense.status][].

        Returns:
            Return the updated data.

        '''
        return ExpenseDB().find_one_and_update(
            {'_id': expense_id},
            {'$set': {'status': status.strip()}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_enable(expense_id: str, enable: bool) -> dict[str, Any]:
        ''' update enable

        Args:
            expense_id (str): The expense id is the unique `_id`.
            enable (bool): update the enable.

        Returns:
            Return the updated data.

        '''
        return ExpenseDB().find_one_and_update(
            {'_id': expense_id},
            {'$set': {'enable': bool(enable)}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_bank(expense_id: str, bank: dict[str, Any]) -> dict[str, Any]:
        ''' Update bank info

        Args:
            expense_id (str): The expense id is the unique `_id`.
            bank (dict): The user's bank info.

        Returns:
            Return the updated data.

        '''
        data = {}
        for key in ('branch', 'code', 'name', 'no'):
            data[key] = bank[key].strip()

        return ExpenseDB().find_one_and_update(
            {'_id': expense_id},
            {'$set': {'bank': data}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_request(expense_id: str, rdata: dict[str, Any]) -> dict[str, Any]:
        '''  update partially

        Args:
            expense_id (str): The expense id is the unique `_id`.
            rdata (dict): The request data partially.

        Returns:
            Return the updated data.

        '''
        return ExpenseDB().find_one_and_update(
            {'_id': expense_id},
            {'$set': {
                'request.desc': rdata['desc'].strip(),
                'request.paydate': rdata['paydate'].strip(),
            }},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_by_create_by(pid: str, create_by: str) -> Cursor[dict[str, Any]]:
        ''' Get by create_by

        Args:
            pid (str): Project id.
            create_by (str): Created by.

        Returns:
            Return the datas in [pymongo.cursor.Cursor][].

        '''
        return ExpenseDB().find({'pid': pid, 'create_by': create_by, 'enable': True})

    @staticmethod
    def get_by_dispense_id (dispense_ids: list[str]) -> Cursor[dict[str, Any]]:
        ''' Retrieve by dispense_id

        Args:
            dispense_ids (list[str]): list of dispense id

        Returns:
            Return the datas in [pymongo.cursor.Cursor][].
        '''
        return ExpenseDB().find({'dispense_id': { '$in': dispense_ids } })

    @staticmethod
    def get_has_sent(pid: str, budget_id: str) -> Generator[dict[str, Any], None, None]:
        ''' Get has sent and not canceled

        Args:
            pid (str): Project id.
            budget_id (str):

        Returns:
            Return the datas in [pymongo.cursor.Cursor][].

        '''
        query = {'pid': pid, 'request.buid': budget_id, 'enable': True}
        for raw in ExpenseDB().find(query, {'invoices': 1, 'code': 1}):
            yield raw

    @staticmethod
    def dl_format(pid: str) -> list[dict[str, Any]]:
        ''' Make the download format(CSV)

        The fields datas:

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

        TODO:
            Get `會計科目` from db

        '''
        raws = []
        for expense in Expense.get_all_by_pid(pid=pid):
            if expense['enable'] is False:
                continue

            base = {
                '組別': expense['tid'],
                '申請單狀態': expense['enable'],
                '編號': '',
                '預算項目': '',
                '預算貨幣': '',
                '預算金額': '',
                '會計科目': '',
                '請款狀態': ExpenseDB.status()[expense['status']],
                '申請時間': expense['create_at'],
                '分行名稱': expense['bank']['branch'],
                '分行代碼': expense['bank']['code'],
                '帳戶名稱': expense['bank']['name'],
                '帳號': expense['bank']['no'],
            }

            for budget in BudgetDB().find({'_id': expense['request']['buid']}):
                base['編號'] = budget['bid']
                base['預算項目'] = budget['name']
                base['預算貨幣'] = budget['currency']
                base['預算金額'] = budget['total']

            for invoice in expense['invoices']:
                data = {}
                data.update(base)

                invoice_data = {
                    '單據名稱': invoice['name'],
                    '單據貨幣': invoice['currency'],
                    '單據金額': invoice['total'],
                    '單據是否收到': invoice['received'],
                }

                data.update(invoice_data)
                raws.append(data)

        return raws
