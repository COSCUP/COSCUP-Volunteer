from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from module.budget import Budget
from module.project import Project
from module.team import Team

VIEW_BUDGET = Blueprint('budget', __name__, url_prefix='/budget')


@VIEW_BUDGET.route('/<pid>', methods=('GET', 'POST'))
def by_project_index(pid):
    ''' index '''
    project = Project.get(pid)

    if not project:
        return redirect('/')

    is_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./budget.html', project=project, is_admin=is_admin)

    elif request.method == 'POST':
        data = request.get_json()

        if data['casename'] == 'get':
            teams = []
            for team in Team.list_by_pid(pid=project['_id']):
                teams.append({'name': team['name'], 'tid': team['tid']})
                default_budget = {
                    'bid': '',
                    'uid': '',
                    'name': '',
                    'total': 0,
                    'paydate': '',
                    'desc': '',
                    'estimate': '',
                    'tid': '',
                    'currency': 'TWD',
                }

            items = []
            for item in Budget.get_by_pid(pid=pid):
                if item['enabled']:
                    item['enabled'] = 'true'
                else:
                    item['enabled'] = 'false'

                items.append(item)

            return jsonify({'teams': teams, 'default_budget': default_budget, 'items': items})

        elif data['casename'] == 'add':
            item = Budget.add(pid=pid, tid=data['data']['tid'], data=data['data'])
            return jsonify({'data': item})

        elif data['casename'] == 'edit':
            if data['data']['enabled'] == 'true':
                data['data']['enabled'] = True
            else:
                data['data']['enabled'] = False

            item = Budget.edit(pid=pid, data=data['data'])

            if item['enabled']:
                item['enabled'] = 'true'
            else:
                item['enabled'] = 'false'

            return jsonify({'data': item})

    return jsonify({})

