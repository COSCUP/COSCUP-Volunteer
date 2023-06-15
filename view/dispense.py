'''Dispense'''
import csv
import io

from typing import Any
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
            return handle_update(data)

    return make_response({}, 404)

def handle_update (data: dict[str, Any]) -> ResponseBase:
    ''' handle update to avoid too many return error '''
    result = Dispense.update(data['data']['_id'], data['data'])

    if isinstance(result, int):
        return Response('Invalid parameter', result)

    return jsonify({'result': result})


@VIEW_DISPENSE.route('/<pid>/dl', methods=('GET', 'POST'))
def by_project_dl(pid: str) -> str | ResponseBase:
    ''' Export dispanse by project id '''
    project = Project.get(pid)

    if not project:
        return redirect('/')

    is_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        raws = Dispense.dl_format(pid)

        if not raws:
            return Response('', status=204)

        with io.StringIO() as files:
            csv_writer = csv.DictWriter(files, fieldnames=list(
                raws[0].keys()), quoting=csv.QUOTE_MINIMAL)
            csv_writer.writeheader()
            csv_writer.writerows(raws)

            filename = f"{project.name} 出款單.csv".encode().decode("latin1")

            return Response(
                files.getvalue().encode(encoding="utf-8-sig"),
                mimetype='text/csv',
                headers={'Content-Type': 'charset=utf-8',
                         'Content-disposition': f'attachment; filename={filename}',
                         'x-filename': filename,
                         })

    return Response('', status=204)
