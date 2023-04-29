'''Dispense'''

from flask import (Blueprint, g, jsonify, make_response, redirect, request, Response)
from werkzeug.wrappers import Response as ResponseBase

from module.budget import Budget
from module.expense import Expense
from module.dispense import Dispense
from module.project import Project

VIEW_DISPENSE = Blueprint('dispense', __name__, url_prefix='/dispense')

@VIEW_DISPENSE.route('/<pid>', methods=('POST',))
def by_project_index(pid: str) -> str | ResponseBase:
    ''' Project index '''
    project = Project.get(pid)

    if not project:
        return redirect('/')

    is_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
    if not is_admin:
        # Only admin is allowed to get all dispense at once
        return redirect('/')

    if request.method == 'POST':
        data = request.get_json()

        if data and data['casename'] == 'get':
            datas = list(Dispense.get_all_by_pid(pid=pid))

            return jsonify({'datas': datas, 'status': Expense.status()})

        if data and data['casename'] == 'add':
            dispense = Dispense.create(
                pid=project.id,
                expense_ids=data['data']['expense_ids'],
                dispense_date=data['data']['dispense_date']
            )
            return jsonify({'result': dispense})

        if data and data['casename'] == 'update':
            result = Dispense.update(data['data']['_id'], data['data'])
            ret = result

            if isinstance(result, int):
                ret = Response('Invalid parameter', result)
            else:
                ret = jsonify({'result': result})            
            return ret

    return make_response({}, 404)
