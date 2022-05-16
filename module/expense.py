''' Expense '''
from pymongo.collection import ReturnDocument

from models.budgetdb import BudgetDB
from models.expensedb import ExpenseDB


class Expense:
    ''' Expense class '''
    @staticmethod
    def process_and_add(pid, tid, uid, data):
        ''' Process data from web '''
        save = ExpenseDB.new(pid=pid, tid=tid, uid=uid)

        save['request'] = {
            'buid': data['expense_request']['buid'],
            'desc': data['expense_request']['desc'],
            'paydate': data['expense_request']['paydate'],
            'code': data['expense_request']['code'],
        }

        save['bank'] = {
            'branch': data['bank']['branch'],
            'code': data['bank']['code'],
            'name': data['bank']['name'],
            'no': data['bank']['no'],
        }

        for invoice in data['invoices']:
            save['invoices'].append(
                {
                    'currency': invoice['currency'],
                    'name': invoice['name'],
                    'status': invoice['status'],
                    'total': invoice['total'],
                    'received': False,
                })

        return ExpenseDB().add(data=save)

    @staticmethod
    def status():
        ''' Get status '''
        return ExpenseDB.status()

    @staticmethod
    def get_all_by_pid(pid):
        ''' Get all '''
        for raw in ExpenseDB().find({'pid': pid}):
            yield raw

    @staticmethod
    def update_invoices(expense_id, invoices):
        ''' Only update invoices '''
        _invoices = []
        for invoice in invoices:
            _invoices.append(
                {'currency': invoice['currency'].strip(),
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
    def update_status(expense_id, status):
        ''' update status '''
        return ExpenseDB().find_one_and_update(
            {'_id': expense_id},
            {'$set': {'status': status.strip()}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_by_create_by(pid, create_by):
        ''' Get by create_by '''
        return ExpenseDB().find({'pid': pid, 'create_by': create_by})

    @staticmethod
    def get_has_sent(pid, budget_id):
        ''' Get has sent and not canceled '''
        query = {'pid': pid, 'request.buid': budget_id}
        for raw in ExpenseDB().find(query, {'invoices': 1}):
            yield raw

    @staticmethod
    def dl_format(pid):
        ''' Make the download format(CSV) '''
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
