from pymongo.collection import ReturnDocument

from models.expensedb import ExpenseDB


class Expense(object):
    ''' Expense class '''
    @staticmethod
    def proess_and_add(pid, tid, uid, data):
        ''' Process data from web '''
        save = ExpenseDB.new(pid=pid, tid=tid, uid=uid)

        save['request'] = {
                'buid': data['expense_request']['buid'],
                'desc': data['expense_request']['desc'],
                'paydate': data['expense_request']['paydate'],
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

    def update_status(expense_id, status):
        ''' update status '''
        return ExpenseDB().find_one_and_update(
                {'_id': expense_id},
                {'$set': {'status': status.strip()}},
                return_document=ReturnDocument.AFTER,
            )

