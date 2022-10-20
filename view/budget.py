''' Budget '''
import csv
import io
from typing import Any

from flask import Blueprint, g, jsonify, redirect, render_template, request
from werkzeug.wrappers import Response as ResponseBase

from module.budget import Budget
from module.project import Project
from module.team import Team

VIEW_BUDGET = Blueprint('budget', __name__, url_prefix='/budget')


@VIEW_BUDGET.route('/batch/<pid>', methods=('GET', 'POST'))
def batch(pid: str) -> str | ResponseBase:  # pylint: disable=too-many-branches
    ''' batch upload '''
    project = Project.get(pid)

    if not project:
        return redirect('/')

    is_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./budget_batch.html',
                               project=project.dict(by_alias=True), is_admin=is_admin)

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()

            if data and data.get('casename') == 'get':
                teams = [
                    {'name': team.name, 'tid': team.id}
                    for team in Team.list_by_pid(pid=project.id)
                ]

                return jsonify({'teams': teams})

        if request.files and 'file' in request.files:
            csv_file = list(csv.DictReader(io.StringIO('\n'.join(
                request.files['file'].read().decode('utf8').split('\n')[1:]))))

            result, error_result = Budget.verify_batch_items(items=csv_file)

            dedup_result = []
            dup_bids = []

            # Pylint unnecessary-lambda-assignment / C3001
            # Lambda expression assigned to a variable.
            # Define a function using the "def" keyword instead.
            def has_bid_in_budget(bid: str) -> dict[str, Any] | None:
                return Budget.get_by_bid(pid=pid, bid=bid)

            def has_added(item: dict[str, Any]) -> bool:
                return bool(item['action'] == 'add' and has_bid_in_budget(item['bid']))

            def did_update_nonexisted_entry(item: dict[str, Any]) -> bool:
                return \
                    item['action'] == 'update' and not has_bid_in_budget(
                        item['bid'])

            for item in result:
                if has_added(item) or did_update_nonexisted_entry(item):
                    dup_bids.append(item['bid'])
                else:
                    dedup_result.append(item)

            if request.form['casename'] == 'verify':
                return jsonify({
                    'file': csv_file,
                    'confirmed': dedup_result,
                    'error_items': error_result,
                    'dup_bids': dup_bids,
                })

            if request.form['casename'] == 'save':
                for item in dedup_result:
                    if item['action'] == 'add':
                        Budget.add(pid=pid, tid=item['tid'], data=item)
                    elif item['action'] == 'update':
                        budget_id = Budget.get_by_bid(pid=pid, bid=item['bid'])
                        if budget_id:
                            item['_id'] = budget_id
                            Budget.edit(pid=pid, data=item)

    return jsonify({})


@VIEW_BUDGET.route('/<pid>', methods=('GET', 'POST'))
def by_project_index(pid: str) -> str | ResponseBase:
    ''' index '''
    # pylint: disable=too-many-return-statements,too-many-branches
    project = Project.get(pid)

    if not project:
        return redirect('/')

    is_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./budget.html',
                               project=project.dict(by_alias=True), is_admin=is_admin)

    if request.method == 'POST':
        data = request.get_json()

        if data and data['casename'] == 'get':
            teams = []
            for team in Team.list_by_pid(pid=project.id):
                teams.append({'name': team.name, 'tid': team.id})

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

        if data and data['casename'] == 'check_bid':
            return jsonify({'existed': bool(Budget.get_by_bid(pid=pid, bid=data['bid']))})

        if data and data['casename'] == 'add':
            item = Budget.add(
                pid=pid, tid=data['data']['tid'], data=data['data'])
            return jsonify({'data': item})

        if data and data['casename'] == 'edit':
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
