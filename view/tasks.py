''' Tasks '''
from typing import Any

import arrow
from flask import (Blueprint, g, jsonify, make_response, redirect,
                   render_template, request, url_for)
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

from celery_task.task_mail_sys import mail_tasks_star
from module.mattermost_bot import MattermostTools
from module.project import Project
from module.tasks import Tasks, TasksStar
from module.team import Team
from module.users import User
from structs.tasks import TaskItem

VIEW_TASKS = Blueprint('tasks', __name__, url_prefix='/tasks')


@VIEW_TASKS.route('/')
def index() -> ResponseBase:
    ''' Index page '''
    return redirect(url_for('tasks.project', pid='2022', _scheme='https', _external=True))


@VIEW_TASKS.route('/<pid>', methods=('GET', 'POST'))
def project(pid: str) -> str | ResponseBase:
    ''' Project '''
    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
    uid = g.get('user', {}).get('account', {}).get('_id')

    project_info = Project.get(pid=pid)
    if not project_info:
        return Response('404', status=404)

    is_in_project = False
    if uid:
        for _ in Team.participate_in(uid=uid, pid=[pid, ]):
            is_in_project = True
            break

    if request.method == 'GET':
        return render_template('./tasks_project.html', project=project_info.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()

        def page_args(data: dict[str, Any], uid: str) -> None:
            data['_uid'] = uid
            data['_joined'] = False
            data['_login'] = False
            data['_is_in_project'] = is_in_project

            if uid:
                data['_login'] = True

                if uid in data['people']:
                    data['_joined'] = True

        if post_data and post_data['casename'] == 'get':
            datas = []

            for data in Tasks.get_by_pid(pid=pid):
                page_args(data=data, uid=uid)
                datas.append(data)

            is_star = False
            if uid:
                is_star = TasksStar.status(pid, uid)['add']

            return jsonify({'datas': datas, 'is_in_project': is_in_project, 'is_star': is_star})

        if post_data and post_data['casename'] == 'star':
            if not uid:
                return make_response({'info': 'Need login'}, 401)

            result = TasksStar.toggle(pid=pid, uid=uid)

            return jsonify({'is_star': result['add']})

        if post_data and post_data['casename'] == 'join':
            if not uid:
                return make_response({'info': 'Need login'}, 401)

            data = Tasks.join(pid=pid, task_id=post_data['task_id'], uid=uid)
            page_args(data=data, uid=uid)

            return jsonify({'data': data})

        if post_data and post_data['casename'] == 'cancel':
            if not uid:
                return make_response({'info': 'Need login'}, 401)

            data = Tasks.cancel(pid=pid, task_id=post_data['task_id'], uid=uid)
            page_args(data=data, uid=uid)

            return jsonify({'data': data})

        if post_data and post_data['casename'] == 'cancel_user':
            if not uid:
                return make_response({'info': 'Need login'}, 401)

            if not is_in_project:
                return make_response({'info': 'Need as staff'}, 401)

            data = Tasks.cancel(
                pid=pid, task_id=post_data['task_id'], uid=post_data['uid'])
            page_args(data=data, uid=uid)

            return jsonify({'data': data})

        if post_data and post_data['casename'] == 'peoples':
            task_data = Tasks.get_with_pid(pid=pid, _id=post_data['task_id'])
            if not task_data:
                return make_response({}, 404)

            users_info = Tasks.get_peoples_info(
                pid=pid, task_id=post_data['task_id'])

            if not users_info:
                return make_response({}, 404)

            creator = {}
            if task_data:
                user_info = User.get_info(uids=[task_data['created_by'], ])
                creator['name'] = user_info[task_data['created_by']
                                            ]['profile']['badge_name']
                creator['uid'] = task_data['created_by']

                mid = MattermostTools.find_possible_mid(
                    uid=task_data['created_by'])
                if mid:
                    creator['mattermost_uid'] = MattermostTools.find_user_name(
                        mid=mid)

            if not is_in_project:
                return jsonify({'peoples': {}, 'creator': creator})

            peoples = {}
            for uid, user in users_info.items():
                peoples[uid] = {
                    'name': user['profile']['badge_name'],
                    'mail': user['oauth']['email'],
                    'picture': user['oauth']['picture'],
                    'mattermost_uid': None,
                }

                mid = MattermostTools.find_possible_mid(uid=uid)
                if mid:
                    peoples[uid]['mattermost_uid'] = MattermostTools.find_user_name(
                        mid=mid)

            return jsonify({'peoples': peoples, 'creator': creator})

    return make_response({}, 404)


@VIEW_TASKS.route('/<pid>/add', methods=('GET', 'POST'))
@VIEW_TASKS.route('/<pid>/edit/<task_id>', methods=('GET', 'POST'))
def add(pid: str, task_id: str | None = None) -> str | ResponseBase:
    ''' Add '''
    # pylint: disable=too-many-return-statements,too-many-branches
    uid = g.get('user', {}).get('account', {}).get('_id')
    if not uid:
        return make_response({'info': 'Need login'}, 401)

    is_in_project = False
    for _ in Team.participate_in(uid=uid, pid=[pid, ]):
        is_in_project = True
        break

    if not is_in_project:
        return make_response({'info': 'Not in project'}, 401)

    project_info = Project.get(pid=pid)
    if not project_info:
        return Response('404', status=404)

    if request.method == 'GET':
        catelist = Tasks.get_cate(pid=pid)
        return render_template('./tasks_add.html', project=project_info.dict(by_alias=True),
                               catelist=catelist, task_id=task_id)

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'add':
            data = post_data['data']
            task_item = TaskItem(pid=pid, created_by=uid, desc=data['desc'])
            task_item.title = data['title']
            task_item.cate = data['cate']
            task_item.limit = data['limit']

            task_item.starttime = arrow.get(arrow.get(f"{data['date']} {data['starttime']}",
                                            tzinfo='Asia/Taipei').timestamp()).naive
            if 'endtime' in data and data['endtime']:
                task_item.endtime = arrow.get(arrow.get(f"{data['date']} {data['endtime']}",
                                              tzinfo='Asia/Taipei').timestamp()).naive

            if 'task_id' in post_data and post_data['task_id']:
                task_item.id = post_data['task_id']

            raw = Tasks.add(pid=pid,
                            body=task_item.dict(by_alias=True))

            if 'task_id' in post_data and not post_data['task_id']:
                mail_tasks_star.apply_async(
                    kwargs={'pid': pid, 'task_id': raw['_id']})

            return jsonify({'data': raw})

        if post_data and post_data['casename'] == 'del':
            data = Tasks.get_with_pid(pid=pid, _id=post_data['task_id'])
            if not data:
                return make_response({}, 404)

            if data['created_by'] == g.user['account']['_id']:
                Tasks.delete(pid=pid, _id=data['_id'])

        if task_id and post_data and post_data['casename'] == 'get':
            data = Tasks.get_with_pid(pid=pid, _id=task_id)
            if not data:
                return make_response({}, 404)

            starttime_task = arrow.get(data['starttime']).to('Asia/Taipei')
            data['date'] = starttime_task.format('YYYY-MM-DD')
            data['starttime'] = starttime_task.format('HH:mm')

            if data['endtime']:
                endtime_task = arrow.get(data['endtime']).to('Asia/Taipei')
                data['endtime'] = endtime_task.format('HH:mm')

            data['_is_creator'] = g.user['account']['_id'] == data['created_by']

            return jsonify({'data': data})

        return jsonify({})

    return jsonify({})


@VIEW_TASKS.route('/<pid>/r/<task_id>', methods=('GET', 'POST'))
def read(pid: str, task_id: str) -> str | ResponseBase:
    ''' Read '''
    project_info = Project.get(pid=pid)
    if not project_info:
        return Response('404', status=404)

    task = Tasks.get_with_pid(pid=pid, _id=task_id)
    if not task:
        return redirect(url_for('tasks.project', pid=pid, _scheme='https', _external=True))

    task['starttime'] = arrow.get(task['starttime']).to(
        'Asia/Taipei').format('YYYY-MM-DD HH:mm')
    if task['endtime']:
        task['endtime'] = arrow.get(task['endtime']).to(
            'Asia/Taipei').format('YYYY-MM-DD HH:mm')

    uid = g.get('user', {}).get('account', {}).get('_id')
    if request.method == 'GET':
        creator = {}
        user_info = User.get_info(uids=[task['created_by'], ])
        creator['name'] = user_info[task['created_by']]['profile']['badge_name']
        creator['uid'] = task['created_by']

        mid = MattermostTools.find_possible_mid(uid=task['created_by'])
        if mid:
            creator['mattermost_uid'] = MattermostTools.find_user_name(mid=mid)

        return render_template('./tasks_detail.html', task=task, creator=creator, uid=uid)

    if request.method == 'POST':
        if not uid:
            return make_response({'info': 'Need login'}, 401)

        post_data = request.get_json()
        if post_data and post_data['casename'] == 'join':
            Tasks.join(pid=pid, task_id=task['_id'], uid=uid)

        elif post_data and post_data['casename'] == 'cancel':
            Tasks.cancel(pid=pid, task_id=task['_id'], uid=uid)

        return jsonify({})
    return jsonify({})
