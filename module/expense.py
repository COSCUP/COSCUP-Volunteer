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
    def get_by_create_by(pid: str, create_by: str) -> Cursor[dict[str, Any]]:
        ''' Get by create_by

        Args:
            pid (str): Project id.
            create_by (str): Created by.

        Returns:
            Return the datas in [pymongo.cursor.Cursor][].

        '''
        return ExpenseDB().find({'pid': pid, 'create_by': create_by})

    @staticmethod
    def get_has_sent(pid: str, budget_id: str) -> Generator[dict[str, Any], None, None]:
        ''' Get has sent and not canceled

        Args:
            pid (str): Project id.
            budget_id (str):

        Returns:
            Return the datas in [pymongo.cursor.Cursor][].

        '''
        query = {'pid': pid, 'request.buid': budget_id}
        for raw in ExpenseDB().find(query, {'invoices': 1, 'code': 1}):
            yield raw

    @staticmethod
    def dl_format(pid: str) -> list[dict[str, Any]]:
        ''' Make the download format(CSV)

        The fields datas:

            - `request.id`: `expense._id`.
            - `request.pid`: `expense.pid`.
            - `request.tid`: `expense.tid`.
            - `note.user`: `expense.note.myself`.
            - `note.finance`: `expense.note.to_create`.
            - `budget._id`: `expense.request.buid`.
            - `budget.bid`: (no data).
            - `request.desc`: `expense.request.desc`.
            - `request.paydate`: `expense.request.paydate`.
            - `request.status`: `expense.status`.
            - `request.status_text`: `ExpenseDB.status()[expense['status']]`.
            - `request.create_at`: `expense.create_at`.
            - `request.create_by`: `expense.create_by`.

        '''
        raws = []
        for expense in Expense.get_all_by_pid(pid=pid):
            base = {
                'request.id': expense['_id'],
                'request.pid': expense['pid'],
                'request.tid': expense['tid'],
                'note.user': expense['note']['myself'],
                'note.finance': expense['note']['to_create'],
                'budget._id': expense['request']['buid'],
                'budget.bid': '',
                'request.desc': expense['request']['desc'],
                'request.paydate': expense['request']['paydate'],
                'request.status': expense['status'],
                'request.status_text': ExpenseDB.status()[expense['status']],
                'request.create_at': expense['create_at'],
                'request.create_by': expense['create_by'],
            }

            for budget in BudgetDB().find({'_id': expense['request']['buid']}):
                base['budget.bid'] = budget['bid']

            for key in expense['bank']:
                base[f'bank.{key}'] = expense['bank'][key]

            for invoice in expense['invoices']:
                data = {}
                data.update(base)
                invoice_data = {}

                for key in invoice:
                    invoice_data[f'invoice.{key}'] = invoice[key]

                data.update(invoice_data)
                raws.append(data)

        return raws
