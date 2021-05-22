from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from module.budget import Budget
from module.expense import Expense
from module.project import Project
from module.users import User

VIEW_EXPENSE = Blueprint('expense', __name__, url_prefix='/expense')

@VIEW_EXPENSE.route('/<pid>', methods=('GET', 'POST'))
def by_project_index(pid):
    project = Project.get(pid)

    if not project:
        return redirect('/')

    is_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./expense.html', project=project, is_admin=is_admin)

    elif request.method == 'POST':
        data = request.get_json()

        if data['casename'] == 'get':
            datas = list(Expense.get_all_by_pid(pid=pid))

            buids = set()
            uids = set()
            for expense in datas:
                buids.add(expense['request']['buid'])
                uids.add(expense['create_by'])

            budgets = {}
            if buids:
                for raw in Budget.get(buids=list(buids), pid=pid):
                    budgets[raw['_id']] = raw

            users = {}
            if uids:
                user_datas = User.get_info(uids=list(uids))
                for uid in user_datas:
                    users[uid] = {
                            'oauth': user_datas[uid]['oauth'],
                            'profile': {'badge_name': user_datas[uid]['profile']['badge_name']}, }

            return jsonify({'datas': datas, 'budgets': budgets, 'users': users,
                    'status': Expense.status()})

        elif data['casename'] == 'update':
            # update invoices
            Expense.update_invoices(expense_id=data['data']['_id'], invoices=data['data']['invoices'])
            result = Expense.update_status(expense_id=data['data']['_id'], status=data['data']['status'])

            return jsonify({'result': result})

