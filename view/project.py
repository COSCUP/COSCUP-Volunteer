import logging
import csv
import io
import math

import arrow
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

import setting
from celery_task.task_service_sync import service_sync_mattermost_add_channel
from models.oauth_db import OAuthDB
from models.teamdb import TeamMemberChangedDB
from models.users_db import UsersDB
from module.dietary_habit import DietaryHabit
from module.form import Form
from module.form import FormAccommodation
from module.form import FormTrafficFeeMapping
from module.mattermost_bot import MattermostBot
from module.mattermost_bot import MattermostTools
from module.project import Project
from module.team import Team
from module.users import User


VIEW_PROJECT = Blueprint('project', __name__, url_prefix='/project')


@VIEW_PROJECT.route('/')
def index():
    projects = []
    data = list(Project.all())
    for d in data:
        date = arrow.get(d['action_date'])
        d['action_date_str'] = '%s (%s)' % (date.format('YYYY-MM-DD'), date.humanize(arrow.now()))

    per = 3
    for i in range(int(math.ceil(len(data) / float(per)))):
        projects.append(data[per*i:min([per*(i+1), len(data)])])

    return render_template('./project_index.html', projects=projects)

@VIEW_PROJECT.route('/<pid>/edit', methods=('GET', 'POST'))
def project_edit(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        if 'volunteer_certificate_hours' not in project:
            project['volunteer_certificate_hours'] = 0

        return render_template('./project_edit.html', project=project)

    elif request.method == 'POST':
        data = {
            'desc': request.form['desc'].strip(),
            'name': request.form['name'].strip(),
            'volunteer_certificate_hours': max([0, int(request.form['volunteer_certificate_hours'])]),
            'calendar': request.form['calendar'].strip(),
            'mailling_staff': request.form['mailling_staff'].strip(),
            'mailling_leader': request.form['mailling_leader'].strip(),
            'shared_drive': request.form['shared_drive'].strip(),
            'mattermost_ch_id': request.form['mattermost_ch_id'].strip(),
            'traffic_fee_doc': request.form['traffic_fee_doc'].strip(),
            'gitlab_project_id': request.form['gitlab_project_id'].strip(),
        }
        Project.update(pid, data)
        return redirect(url_for('project.project_edit', pid=pid, _scheme='https', _external=True))

@VIEW_PROJECT.route('/<pid>/edit/team', methods=('GET', 'POST'))
def project_edit_create_team(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    teams = Team.list_by_pid(project['_id'], show_all=True)
    return render_template('./project_edit_create_team.html', project=project, teams=teams)

@VIEW_PROJECT.route('/<pid>/form', methods=('GET', 'POST'))
def project_form(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./project_form.html', project=project)

@VIEW_PROJECT.route('/<pid>/form/api', methods=('GET', 'POST'))
def project_form_api(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'POST':
        data = request.get_json()
        if 'case' not in data:
            return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

        if data['case'] == 'volunteer_certificate':
            fieldnames = ('uid', 'picture', 'value', 'name', 'roc_id', 'birthday', 'company')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_volunteer_certificate(pid):
                    user_info = UsersDB().find_one({'_id': raw['uid']})
                    oauth = OAuthDB().find_one({'owner': raw['uid']}, {'data.picture': 1})

                    data = {
                        'uid': raw['uid'],
                        'picture': oauth['data']['picture'],
                        'value': raw['data']['value'],
                        'name': user_info['profile_real']['name'],
                        'roc_id': user_info['profile_real']['roc_id'],
                        'birthday': user_info['profile_real']['birthday'],
                        'company': user_info['profile_real']['company'],
                    }

                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

        elif data['case'] == 'traffic_fee':
            fieldnames = ('uid', 'picture', 'name', 'apply', 'fee', 'fromwhere', 'howto')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_traffic_fee(pid):
                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    data = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'apply': raw['data']['apply'],
                        'fee': raw['data']['fee'],
                        'fromwhere': raw['data']['fromwhere'],
                        'howto': raw['data']['howto'],
                    }

                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

        elif data['case'] == 'accommodation':
            fieldnames = ('uid', 'picture', 'name', 'key', 'status')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_accommodation(pid):
                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    data = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'key': raw['data']['key'],
                        'status': raw['data']['status'],
                    }

                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

        elif data['case'] == 'appreciation':
            fieldnames = ('uid', 'picture', 'name', 'available', 'key', 'value')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_appreciation(pid):
                    if not raw['data']['available']:
                        continue

                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    data = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'available': raw['data']['available'],
                        'key': raw['data']['key'],
                        'value': raw['data']['value'],
                    }
                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

        elif data['case'] == 'clothes':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                for uid in team['chiefs']+team['members']:
                    all_users[uid] = {'tid': team['tid']}

            user_info = User.get_info(uids=list(all_users.keys()))

            fieldnames = ('uid', 'picture', 'name', '_has_data', 'tid', 'clothes')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_clothes(pid):
                    if raw['uid'] not in all_users:
                        continue
                    all_users[raw['uid']]['clothes'] = raw['data']['clothes']

                for uid in all_users:
                    data = {
                        'uid': uid,
                        'picture': user_info[uid]['oauth']['picture'],
                        'name': user_info[uid]['profile']['badge_name'],
                        '_has_data': bool(all_users[uid].get('clothes', False)),
                        'tid': all_users[uid]['tid'],
                        'clothes': all_users[uid].get('clothes'),
                    }
                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

        elif data['case'] == 'parking_card':
            fieldnames = ('uid', 'picture', 'name', 'carno', 'dates')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_parking_card(pid):
                    if not raw['data']['dates']:
                        continue

                    user_info = User.get_info(uids=[raw['uid'], ])[raw['uid']]

                    data = {
                        'uid': raw['uid'],
                        'picture': user_info['oauth']['picture'],
                        'name': user_info['profile']['badge_name'],
                        'carno': raw['data']['carno'],
                        'dates': ', '.join(raw['data']['dates']),
                    }
                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

        elif data['case'] == 'drink':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                for uid in team['chiefs']+team['members']:
                    all_users[uid] = {'tid': team['tid']}

            user_info = User.get_info(uids=list(all_users.keys()))

            fieldnames = ('uid', 'picture', 'name', '_has_data', 'tid', 'y18')
            with io.StringIO() as str_io:
                csv_writer = csv.DictWriter(str_io, fieldnames=fieldnames)
                csv_writer.writeheader()

                for raw in Form.all_drink(pid):
                    if raw['uid'] not in all_users:
                        continue

                    all_users[raw['uid']]['y18'] = raw['data']['y18']

                for uid in all_users:
                    data = {
                        'uid': uid,
                        'picture': user_info[uid]['oauth']['picture'],
                        'name': user_info[uid]['profile']['badge_name'],
                        '_has_data': True if all_users[uid].get('y18') is not None else False,
                        'tid': all_users[uid]['tid'],
                        'y18': all_users[uid].get('y18'),
                    }
                    csv_writer.writerow(data)

                result = []
                for raw in csv.reader(io.StringIO(str_io.getvalue())):
                    result.append(raw)

                return jsonify({'result': result})

@VIEW_PROJECT.route('/<pid>/edit/team/api', methods=('GET', 'POST'))
def project_edit_create_team_api(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        _team = Team.get(pid, request.args['tid'].strip())
        team = {}
        for k in ('name', 'chiefs', 'members', 'owners', 'tid', 'headcount', 'mailling', 'disabled'):
            if k in _team:
                team[k] = _team[k]

        if 'headcount' not in team:
            team['headcount'] = 0
        else:
            team['headcount'] = max([0, int(team['headcount'])])

        return jsonify(team)

    elif request.method == 'POST':
        data = request.json
        if data['submittype'] == 'update':
            chiefs = data['chiefs']
            members = data['members']
            if isinstance(data['chiefs'], str):
                chiefs = data['chiefs'].split(',')

            if isinstance(data['members'], str):
                members = data['members'].split(',')

            new_members = set(chiefs + members)
            old_members = set(Team.get_users(pid=pid, tids=(data['tid'], ))[data['tid']])

            TeamMemberChangedDB().make_record(pid=pid, tid=data['tid'],
                    add_uids=new_members-old_members, del_uids=old_members-new_members)

            Team.update_setting(pid=pid, tid=data['tid'], data=data)
            service_sync_mattermost_add_channel.apply_async(kwargs={'pid': pid, 'uids': list(new_members)})

            return u'%s' % data
        elif data['submittype'] == 'create':
            Team.create(pid=pid, tid=data['tid'], name=data['name'], owners=project['owners'])
            return u'%s' % data

@VIEW_PROJECT.route('/<pid>/')
def team_page(pid):
    teams = []
    project = Project.get(pid)
    if not project:
        return u'no data', 404

    data = list(Team.list_by_pid(project['_id']))
    uids = []
    for t in data:
        uids.extend(t['chiefs'])

    total = 0
    user_info = User.get_info(uids)
    for t in data:
        t['chiefs_name'] = []
        for uid in t['chiefs']:
            t['chiefs_name'].append('<a href="/user/%s">%s</a>' % (uid, user_info[uid]['profile']['badge_name']))

        t['count'] = len(set(t['chiefs'] + t['members']))
        total += t['count']

    # ----- group for layout ----- #
    per = 3
    for i in range(int(math.ceil(len(data) / float(per)))):
        teams.append(data[per*i:min([per*(i+1), len(data)])])

    editable = g.user['account']['_id'] in project['owners']

    return render_template('./project_teams_index.html',
        teams=teams,
        project=project,
        editable=editable,
        total=total,
    )

@VIEW_PROJECT.route('/<pid>/form_traffic_mapping', methods=('GET', 'POST'))
def project_form_traffic_mapping(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./project_form_traffic_mapping.html', project=project)

    elif request.method == 'POST':
        data = request.get_json()
        if 'casename' in data and data['casename'] == 'init':
            return jsonify({
                'base': {'loaction': '', 'fee': 0},
                'data': (FormTrafficFeeMapping.get(pid=pid) or {}).get('data', []),
            })

        if 'casename' in data and data['casename'] == 'save':
            feemapping = {}
            for raw in data['data']:
                if raw['location'].strip():
                    feemapping[raw['location'].strip()] = raw['fee']

            result = FormTrafficFeeMapping.save(pid=pid, data=feemapping)
            return jsonify({'data': result['data']})

@VIEW_PROJECT.route('/<pid>/form/accommodation', methods=('GET', 'POST'))
def project_form_accommodation(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./project_form_accommodation.html', project=project)

    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                for uid in team['chiefs']+team['members']:
                    all_users[uid] = {'tid': team['tid']}

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

        elif post_data['casename'] == 'update':
            for data in post_data['datas']:
                logging.info('uid: %s, room: %s', data['uid'].strip(), data['room'].strip())
                FormAccommodation.update_room(
                        pid=pid, uid=data['uid'].strip(), room=data['room'].strip())

            return jsonify({})

@VIEW_PROJECT.route('/<pid>/dietary_habit', methods=('GET', 'POST'))
def project_dietary_habit(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./project_dietary_habit.html', project=project)

    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                for uid in team['chiefs']+team['members']:
                    all_users[uid] = {'tid': team['tid']}

            user_infos = User.get_info(uids=list(all_users.keys()), need_sensitive=True)

            datas = []
            for uid in all_users:
                user_info = user_infos[uid]
                data = {
                    'uid': uid,
                    'name': user_info['profile']['badge_name'],
                    'picture': user_info['oauth']['picture'],
                    'tid': all_users[uid]['tid'],
                    'dietary_habit': [],
                }

                if 'profile_real' in user_info and 'dietary_habit' in user_info['profile_real']:
                    data['dietary_habit'] = user_info['profile_real']['dietary_habit']

                datas.append(data)

            return jsonify({'datas': datas, 'dietary_habit': DietaryHabit.ITEMS})

@VIEW_PROJECT.route('/<pid>/contact_book', methods=('GET', 'POST'))
def project_contact_book(pid):
    project = Project.get(pid)
    if g.user['account']['_id'] not in project['owners']:
        return redirect(url_for('project.team_page', pid=pid, _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./project_contact_book.html', project=project)

    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            all_users = {}
            for team in Team.list_by_pid(pid=pid):
                for uid in team['chiefs']+team['members']:
                    all_users[uid] = {'tid': team['tid']}

            user_infos = User.get_info(uids=list(all_users.keys()), need_sensitive=True)

            mmb = MattermostBot(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
            mmt = MattermostTools(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
            datas = []
            for uid in all_users:
                user_info = user_infos[uid]
                data = {
                    'uid': uid,
                    'name': user_info['profile']['badge_name'],
                    'picture': user_info['oauth']['picture'],
                    'tid': all_users[uid]['tid'],
                    'email': user_info['oauth']['email'],
                }

                if 'profile_real' in user_info:
                    data['phone'] = user_info['profile_real'].get('phone', '')

                data['user_name'] = mmt.find_user_name(mmt.find_possible_mid(uid=uid))
                datas.append(data)

            return jsonify({'datas': datas})
