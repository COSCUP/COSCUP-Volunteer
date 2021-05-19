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

