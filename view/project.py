''' Project '''
import csv
import io
import logging
import math
from typing import Any, Literal, Mapping

import arrow
from flask import (Blueprint, g, jsonify, make_response, redirect,
                   render_template, request, url_for)
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

import setting
from celery_task.task_service_sync import service_sync_mattermost_add_channel
from models.oauth_db import OAuthDB
from models.teamdb import TeamMemberChangedDB
from models.users_db import UsersDB
from module.dietary_habit import DietaryHabitItemsName, DietaryHabitItemsValue
from module.form import Form, FormAccommodation, FormTrafficFeeMapping
from module.mattermost_bot import MattermostTools
from module.project import Project
from module.team import Team
from module.users import User
from structs.projects import (FormsSwitch, ProjectBaseUpdate,
                              ProjectTrafficLocationFeeItem)

VIEW_PROJECT = Blueprint('project', __name__, url_prefix='/project')


@VIEW_PROJECT.route('/')
def index() -> str:
    ''' Index page '''
    projects = []
    datas = []
    for project in Project.all():
        datas.append(project.dict(by_alias=True))

    for data in datas:
        date = arrow.get(data['action_date'])
        data['action_date_str'] = f"{date.format('YYYY-MM-DD')} ({date.humanize(arrow.now())})"

    per = 3
    for i in range(int(math.ceil(len(datas) / float(per)))):
        projects.append(datas[per*i:min([per*(i+1), len(datas)])])

    return render_template('./project_index.html', projects=projects)


@VIEW_PROJECT.route('/<pid>/edit', methods=('GET', 'POST'))
def project_edit(pid: str) -> str | ResponseBase:
    ''' Project edit '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project and request.method == 'GET':
        return render_template('./project_edit.html', project=project.dict(by_alias=True))

    if request.method == 'POST':
        data: dict[str, Any] = dict(request.form)
        data['formswitch'] = FormsSwitch().dict()
        for key in data:
            if key.startswith('formswitch.'):
                item = key.split('.')[1]
                data['formswitch'][item] = True

        Project.update(pid, ProjectBaseUpdate.parse_obj(data))
        return redirect(url_for('project.project_edit', pid=pid, _scheme='https', _external=True))

    return Response('', status=404)


@VIEW_PROJECT.route('/<pid>/edit/team', methods=('GET', 'POST'))
def project_edit_create_team(pid: str) -> str | ResponseBase:
    ''' Project edit create team '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project:
        teams = []
        for team in Team.list_by_pid(project.id, show_all=True):
            teams.append(team.dict(by_alias=True))

        return render_template('./project_edit_create_team.html',
                               project=project.dict(by_alias=True), teams=teams)

    return Response('', status=404)


@VIEW_PROJECT.route('/<pid>/form', methods=('GET', 'POST'))
def project_form(pid: str) -> str | ResponseBase:
    ''' Project form '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project and request.method == 'GET':
        return render_template('./project_form.html', project=project.dict(by_alias=True))

    return Response('', status=404)


@VIEW_PROJECT.route('/<pid>/form/api', methods=('GET', 'POST'))
def project_form_api(pid: str) -> str | ResponseBase:  # pylint: disable=too-many-locals
    ''' Project form API '''
    # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'POST':
        data = request.get_json()
        if data and 'case' not in data:
            return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

        if data and data['case'] == 'volunteer_certificate':
            fieldnames = ('uid', 'picture', 'value', 'name',
                          'roc_id', 'birthday', 'company')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                row_data: Mapping[Literal['uid', 'picture', 'value',
                                          'name', 'roc_id', 'birthday',
                                          'company'], str] | Mapping[str, Any]
                for raw in Form.all_volunteer_certificate(pid):
                    user_info = UsersDB().find_one({'_id': raw['uid']})
                    if not user_info:
                        continue

                    oauth = OAuthDB().find_one(
                        {'owner': raw['uid']}, {'data.picture': 1})
                    if not oauth:
                        continue

                    row_data = {
                        'uid': raw['uid'],
                        'picture': oauth['data']['picture'],
                        'value': raw['data']['value'],
                        'name': user_info['profile_real']['name'],
                        'roc_id': user_info['profile_real']['roc_id'],
                        'birthday': user_info['profile_real']['birthday'],
                        'company': user_info['profile_real']['company'],
                    }

                    csv_writer.writerow(row_data)

                result = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw_read)

                return jsonify({'result': result})

        if data and data['case'] == 'traffic_fee':
            fieldnames = ('uid', 'picture', 'name', 'apply',
                          'fee', 'fromwhere', 'howto')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                row_data_traffic: Mapping[Literal['uid', 'picture', 'name',
                                          'apply', 'fee', 'fromwhere', 'howto'],
                                          str] | Mapping[str, Any]
                for raw in Form.all_traffic_fee(pid):
                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]
                    if not user_info:
                        continue

                    row_data_traffic = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'apply': raw['data']['apply'],
                        'fee': raw['data']['fee'],
                        'fromwhere': raw['data']['fromwhere'],
                        'howto': raw['data']['howto'],
                    }

                    csv_writer.writerow(row_data_traffic)

                result = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw_read)

                return jsonify({'result': result})

        if data and data['case'] == 'accommodation':
            fieldnames_acc = ('uid', 'picture', 'name', 'key', 'status')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames_acc)
                csv_writer.writeheader()

                row_data_acc: Mapping[Literal['uid',
                                              'picture', 'name', 'key',
                                              'status'], str] | Mapping[str, Any]
                for raw in Form.all_accommodation(pid):
                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    if not user_info:
                        continue

                    row_data_acc = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'key': raw['data']['key'],
                        'status': raw['data']['status'],
                    }

                    csv_writer.writerow(row_data_acc)

                result = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw_read)

                return jsonify({'result': result})

        if data and data['case'] == 'appreciation':
            fieldnames_app = ('uid', 'picture', 'name',
                              'available', 'key', 'value')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames_app)
                csv_writer.writeheader()

                row_data_app: Mapping[Literal['uid', 'picture',
                                              'name', 'available',
                                              'key', 'value'], str] | Mapping[str, Any]
                for raw in Form.all_appreciation(pid):
                    if not raw['data']['available']:
                        continue

                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    if not user_info:
                        continue

                    row_data_app = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'available': raw['data']['available'],
                        'key': raw['data']['key'],
                        'value': raw['data']['value'],
                    }
                    csv_writer.writerow(row_data_app)

                result_str = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result_str.append(raw_read)

                return jsonify({'result': result_str})

        if data and data['case'] == 'clothes':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                if team.chiefs:
                    for uid in team.chiefs:
                        all_users[uid] = {'tid': team.id}

                if team.members:
                    for uid in team.members:
                        all_users[uid] = {'tid': team.id}

            user_info = User.get_info(uids=list(all_users.keys()))

            fieldnames = ('uid', 'picture', 'name',
                          '_has_data', 'tid', 'clothes', 'htg')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                row_data_clothes: Mapping[Literal['uid', 'picture',
                                                  'name', '_has_data',
                                                  'tid', 'clothes', 'htg'], str] | Mapping[str, Any]
                for raw in Form.all_clothes(pid):
                    if raw['uid'] not in all_users:
                        continue

                    all_users[raw['uid']]['clothes'] = raw['data']['clothes']

                    if 'htg' in raw['data']:
                        all_users[raw['uid']]['htg'] = raw['data']['htg']

                for uid, value in all_users.items():
                    row_data_clothes = {
                        'uid': uid,
                        'picture': user_info[uid]['oauth']['picture'],
                        'name': user_info[uid]['profile']['badge_name'],
                        '_has_data': bool(value.get('clothes', False)),
                        'tid': value['tid'],
                        'clothes': value.get('clothes'),
                        'htg': value.get('htg'),
                    }
                    csv_writer.writerow(row_data_clothes)

                result = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw_read)

                return jsonify({'result': result})

        if data and data['case'] == 'parking_card':
            fieldnames_parking = ('uid', 'picture', 'name', 'carno', 'dates')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(
                    str_io, fieldnames=fieldnames_parking)
                csv_writer.writeheader()

                row_data_parking: Mapping[Literal['uid', 'picture',
                                                  'name', 'carno',
                                                  'dates'], str] | Mapping[str, Any]
                for raw in Form.all_parking_card(pid):
                    if not raw['data']['dates']:
                        continue

                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    if not user_info:
                        continue

                    row_data_parking = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'carno': raw['data']['carno'],
                        'dates': ', '.join(raw['data']['dates']),
                    }
                    csv_writer.writerow(row_data_parking)

                result = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw_read)

                return jsonify({'result': result})

        if data and data['case'] == 'drink':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                if team.chiefs:
                    for uid in team.chiefs:
                        all_users[uid] = {'tid': team.id}

                if team.members:
                    for uid in team.members:
                        all_users[uid] = {'tid': team.id}

            user_info = User.get_info(uids=list(all_users.keys()))

            fieldnames_drink = ('uid', 'picture', 'name',
                                '_has_data', 'tid', 'y18')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(
                    str_io, fieldnames=fieldnames_drink)
                csv_writer.writeheader()

                row_data_drink: Mapping[Literal['uid', 'picture', 'name',
                                                '_has_data', 'tid', 'y18'], str] | Mapping[str, Any]
                for raw in Form.all_drink(pid):
                    if raw['uid'] not in all_users:
                        continue

                    all_users[raw['uid']]['y18'] = raw['data']['y18']

                for uid, value in all_users.items():
                    row_data_drink = {
                        'uid': uid,
                        'picture': user_info[uid]['oauth']['picture'],
                        'name': user_info[uid]['profile']['badge_name'],
                        '_has_data': bool(value.get('y18')),
                        'tid': value['tid'],
                        'y18': value.get('y18'),
                    }
                    csv_writer.writerow(row_data_drink)

                result = []
                for raw_read in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw_read)

                return jsonify({'result': result})

    return make_response({}, 404)


@VIEW_PROJECT.route('/<pid>/edit/team/api', methods=('GET', 'POST'))
def project_edit_create_team_api(pid: str) -> ResponseBase:  # pylint: disable=too-many-branches
    ''' Project edit create team API '''
    project = Project.get(pid)
    if not project or not project.owners or g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        _data = Team.get(pid, request.args['tid'].strip())
        if _data is not None:
            _team = _data.dict(by_alias=True)

            team = {}
            for k in ('name', 'chiefs', 'members', 'owners', 'tid',
                      'headcount', 'mailling', 'disabled'):
                if k in _team:
                    team[k] = _team[k]

            if 'headcount' not in team or team['headcount'] is None:
                team['headcount'] = 0
            else:
                team['headcount'] = max([0, int(team['headcount'])])

            return jsonify(team)

    if request.method == 'POST':
        data = request.json
        if data and data['submittype'] == 'update':
            chiefs = data['chiefs']
            members = data['members']
            if isinstance(data['chiefs'], str):
                chiefs = [_uid.strip()
                          for _uid in data['chiefs'].split(',') if _uid.strip()]

            if isinstance(data['members'], str):
                members = [_uid.strip()
                           for _uid in data['members'].split(',') if _uid.strip()]

            if chiefs is None:
                chiefs = []

            if members is None:
                members = []

            new_members = set(chiefs + members)
            old_members = set(Team.get_users(
                pid=pid, tids=[data['tid'], ])[data['tid']])

            TeamMemberChangedDB().make_record(pid=pid, tid=data['tid'],
                                              action={'add': list(new_members-old_members),
                                                      'del': list(old_members-new_members)})

            Team.update_setting(pid=pid, tid=data['tid'], data=data)
            service_sync_mattermost_add_channel.apply_async(
                kwargs={'pid': pid, 'uids': list(new_members)})

            return Response(f'{data}')

        if data and data['submittype'] == 'create':
            Team.create(
                pid=pid, tid=data['tid'], name=data['name'], owners=project.owners)
            return Response(f'{data}')

    return Response('', status=404)


@VIEW_PROJECT.route('/<pid>/')
def team_page(pid: str) -> str | ResponseBase:
    ''' Team page '''
    teams = []
    project = Project.get(pid)
    if not project:
        return Response('no data', status=404)

    data = [team.dict(by_alias=True) for team in Team.list_by_pid(project.id)]
    uids = []
    for team in data:
        if team['chiefs']:
            uids.extend(team['chiefs'])

    total = 0
    user_info = User.get_info(uids)
    for team in data:
        team['chiefs_name'] = []
        if team['chiefs']:
            for uid in team['chiefs']:
                team['chiefs_name'].append(
                    f'''<a href="/user/{uid}">{user_info[uid]['profile']['badge_name']}</a>''')

        team_uids = set()
        if team['chiefs']:
            team_uids.update(team['chiefs'])
        if team['members']:
            team_uids.update(team['members'])

        team['count'] = len(team_uids)
        total += team['count']

    # ----- group for layout ----- #
    per = 3
    for i in range(int(math.ceil(len(data) / float(per)))):
        teams.append(data[per*i:min([per*(i+1), len(data)])])

    editable = g.user['account']['_id'] in project.owners

    return render_template('./project_teams_index.html',
                           teams=teams,
                           project=project.dict(by_alias=True),
                           editable=editable,
                           total=total,
                           )


@VIEW_PROJECT.route('/<pid>/form_traffic_mapping', methods=('GET', 'POST'))
def project_form_traffic_mapping(pid: str) -> str | ResponseBase:
    ''' Project form traffic mapping '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project and request.method == 'GET':
        return render_template('./project_form_traffic_mapping.html',
                               project=project.dict(by_alias=True))

    if request.method == 'POST':
        data = request.get_json()
        if data and 'casename' in data and data['casename'] == 'init':
            return jsonify({
                'base': ProjectTrafficLocationFeeItem().dict(),
                'data': {item.location: item.fee for item in FormTrafficFeeMapping.get(pid=pid)},
            })

        if data and 'casename' in data and data['casename'] == 'save':
            feemapping = []
            for raw in data['data']:
                if raw['location'].strip():
                    feemapping.append(
                        ProjectTrafficLocationFeeItem.parse_obj(raw))

            saved = FormTrafficFeeMapping.save(pid=pid, datas=feemapping)
            result = {}
            for item in saved:
                result[item.location] = item.fee

            return jsonify({'data': result})

    return Response('', status=404)


@VIEW_PROJECT.route('/<pid>/form/accommodation', methods=('GET', 'POST'))
def project_form_accommodation(pid: str) -> str | ResponseBase:  # pylint: disable=too-many-branches
    ''' Project form accommodation '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project and request.method == 'GET':
        return render_template('./project_form_accommodation.html',
                               project=project.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                if team.chiefs:
                    for uid in team.chiefs:
                        all_users[uid] = {'tid': team.id}

                if team.members:
                    for uid in team.members:
                        all_users[uid] = {'tid': team.id}

            raws = []
            for raw in FormAccommodation.get(pid):
                if raw['uid'] not in all_users:
                    continue

                raws.append(raw)

            user_infos = User.get_info(
                uids=[raw['uid'] for raw in raws], need_sensitive=True)

            datas = []
            for raw in raws:
                user_info = user_infos[raw['uid']]
                datas.append({
                    'uid': raw['uid'],
                    'name': user_info['profile']['badge_name'],
                    'picture': user_info['oauth']['picture'],
                    'roc_id': user_info['profile_real']['roc_id'],
                    'tid': all_users[raw['uid']]['tid'],
                    'room': raw['data'].get('room', ''),
                    'room_key': raw['data'].get('room_key', ''),
                    'data': raw['data'],
                })

            return jsonify({'datas': datas})

        if post_data and post_data['casename'] == 'update':
            for data in post_data['datas']:
                logging.info('uid: %s, room: %s',
                             data['uid'].strip(), data['room'].strip())
                FormAccommodation.update_room(
                    pid=pid, uid=data['uid'].strip(), room=data['room'].strip())

            return jsonify({})

    return make_response({}, 404)


@VIEW_PROJECT.route('/<pid>/dietary_habit', methods=('GET', 'POST'))
def project_dietary_habit(pid: str) -> str | ResponseBase:
    ''' Project dietary habit '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project and request.method == 'GET':
        return render_template('./project_dietary_habit.html',
                               project=project.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                if team.chiefs:
                    for uid in team.chiefs:
                        all_users[uid] = {'tid': team.id}

                if team.members:
                    for uid in team.members:
                        all_users[uid] = {'tid': team.id}

            user_infos = User.get_info(
                uids=list(all_users.keys()), need_sensitive=True)

            datas = list(User.marshal_dietary_habit(user_infos=user_infos))
            for data in datas:
                if data['uid'] not in all_users:
                    continue

                data['tid'] = all_users[data['uid']]['tid']

            dietary_habit_list = {}
            for item in DietaryHabitItemsName:
                dietary_habit_list[DietaryHabitItemsValue[item.name].value] = item.value

            return jsonify({'datas': datas, 'dietary_habit': dietary_habit_list})

    return Response('', status=404)


@VIEW_PROJECT.route('/<pid>/contact_book', methods=('GET', 'POST'))
def project_contact_book(pid: str) -> str | ResponseBase:
    ''' Project contact book '''
    project = Project.get(pid)
    if project and g.user['account']['_id'] not in project.owners:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if project and request.method == 'GET':
        return render_template('./project_contact_book.html', project=project.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                if team.chiefs:
                    for uid in team.chiefs:
                        all_users[uid] = {'tid': team.id}

                if team.members:
                    for uid in team.members:
                        all_users[uid] = {'tid': team.id}

            user_infos = User.get_info(
                uids=list(all_users.keys()), need_sensitive=True)

            mmt = MattermostTools(
                token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
            datas = []
            for uid, value in all_users.items():
                user_info = user_infos[uid]
                data = {
                    'uid': uid,
                    'name': user_info['profile']['badge_name'],
                    'picture': user_info['oauth']['picture'],
                    'tid': value['tid'],
                    'email': user_info['oauth']['email'],
                }

                if 'profile_real' in user_info:
                    data['phone'] = user_info['profile_real'].get('phone', '')

                data['user_name'] = mmt.find_user_name(
                    mmt.find_possible_mid(uid=uid))
                datas.append(data)

            return jsonify({'datas': datas})

    return make_response({}, 404)
