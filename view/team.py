import html

from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markdown import markdown

from module.form import Form
from module.project import Project
from module.team import Team
from module.users import User
from module.waitlist import WaitList

VIEW_TEAM = Blueprint('team', __name__, url_prefix='/team')


@VIEW_TEAM.route('/<pid>/<tid>/')
def index(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(pid)
    if not project:
        return redirect('/')

    for k in ('desc', 'public_desc'):
        if k not in team:
            team[k] = ''
        else:
            team[k] = markdown(html.escape(team[k]))

    preview_public = False
    if 'preview' in request.args:
        preview_public = True

    join_able = not (g.user['account']['_id'] in team['members'] or \
                     g.user['account']['_id'] in team['chiefs'] or \
                     g.user['account']['_id'] in team['owners'] or \
                     g.user['account']['_id'] in project['owners'])

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    return render_template('./team_index.html', team=team, project=project,
            join_able=join_able, is_admin=is_admin, preview_public=preview_public)

@VIEW_TEAM.route('/<pid>/<tid>/edit', methods=('GET', 'POST'))
def team_edit(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(pid)
    if not project:
        return redirect('/')

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./team_edit_setting.html', project=project, team=team)

    elif request.method == 'POST':
        data = {
          'name': request.form['name'].strip(),
          'public_desc': request.form['public_desc'].strip(),
          'desc': request.form['desc'].strip(),
        }
        Team.update_setting(pid=team['pid'], tid=team['tid'], data=data)
        return redirect(url_for('team.team_edit', pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))

@VIEW_TEAM.route('/<pid>/<tid>/edit_user', methods=('GET', 'POST'))
def team_edit_user(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(pid)
    if not project:
        return redirect('/')

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        waitting_list = list(WaitList.list_by_team(pid=pid, tid=tid))
        uids = [u['uid'] for u in waitting_list]
        users_info = User.get_info(uids)

        for u in waitting_list:
            u['_info'] = users_info[u['uid']]

        members = []
        if team['members'] or team['chiefs']:
            _all_uids = set(team['chiefs']) | set(team['members'])
            users_info = User.get_info(list(_all_uids))
            for uid in _all_uids:
                members.append(users_info[uid])

            sorted(members, key=lambda u: u['profile']['badge_name'])

        return render_template('./team_edit_user.html',
                project=project, team=team, waitting_list=waitting_list, members=members)

    elif request.method == 'POST':
        data = request.json

        if data['case'] == 'deluser':
            Team.update_members(pid=pid, tid=tid, del_uids=[data['uid'], ])

        return jsonify(data)

@VIEW_TEAM.route('/<pid>/<tid>/edit_user/api', methods=('GET', 'POST'))
def team_edit_user_api(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(pid)
    if not project:
        return redirect('/')

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        user = User(uid=request.args['uid']).get()
        user_waitting = WaitList.list_by_team(pid=pid, tid=tid, uid=user['_id'])
        if not user_waitting:
            return jsonify({})

        users_info = User.get_info([user['_id'], ])

        user_data = {
            'badge_name': users_info[user['_id']]['profile']['badge_name'],
            'picture': users_info[user['_id']]['oauth']['picture'],
            'uid': user['_id'],
            'note': user_waitting['note'],
            'wid': u'%(_id)s' % user_waitting,
        }

        return jsonify(user_data)

    elif request.method == 'POST':
        all_members = len(team['members']) + len(team['chiefs'])
        if 'headcount' in team and team['headcount'] and all_members >= team['headcount']:
            return jsonify({'status': 'fail', 'message': 'over headcount.'}), 406

        data = request.json
        w = WaitList.make_result(wid=data['wid'], pid=pid, uid=data['uid'], result=data['result'])
        if w and 'result' in w and w['result'] == 'approval':
            Team.update_members(pid=pid, tid=tid, add_uids=[data['uid'], ])

        return jsonify({'status': 'ok'})

@VIEW_TEAM.route('/<pid>/<tid>/join_to', methods=('GET', 'POST'))
def team_join_to(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(team['pid'])
    if not project:
        return redirect('/')

    if g.user['account']['_id'] in team['members'] or g.user['account']['_id'] in team['chiefs']:
        return redirect(url_for('team.index', pid=pid, tid=tid))

    if request.method == 'GET':
        is_in_wait = WaitList.is_in_wait(pid=team['pid'], tid=team['tid'], uid=g.user['account']['_id'])
        return render_template('./team_join_to.html', project=project, team=team, is_in_wait=is_in_wait)

    elif request.method == 'POST':
        WaitList.join_to(pid=pid, tid=tid, uid=g.user['account']['_id'], note=request.form['note'].strip())
        return redirect(url_for('team.team_join_to', pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))

@VIEW_TEAM.route('/<pid>/<tid>/form/api', methods=('GET', 'POST'))
def team_form_api(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(team['pid'])
    if not project:
        return redirect('/')

    if request.method == 'GET':
        if request.args['case'] == 'locations':
            return jsonify({'locations': ['TW', 'JP']})

        return jsonify(request.args)

@VIEW_TEAM.route('/<pid>/<tid>/form/accommodation', methods=('GET', 'POST'))
def team_form_accommodation(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(team['pid'])
    if not project:
        return redirect('/')

    is_ok_submit = False
    user = User(uid=g.user['account']['_id']).get()
    if 'profile_real' in user and 'name' in user['profile_real'] and 'roc_id' in user['profile_real']:
        if user['profile_real']['name'] and user['profile_real']['roc_id']:
            is_ok_submit = True

    if request.method == 'GET':
        return render_template('./form_accommodation.html', project=project, team=team, is_ok_submit=is_ok_submit)

    elif request.method == 'POST':
        if not is_ok_submit:
            return u'', 406

        return u'%s' % request.form

@VIEW_TEAM.route('/<pid>/<tid>/form/traffic_fee', methods=('GET', 'POST'))
def team_form_traffic_fee(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(team['pid'])
    if not project:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_traffic_fee.html', project=project, team=team)

    elif request.method == 'POST':
        return u'%s' % request.form

@VIEW_TEAM.route('/<pid>/<tid>/form/volunteer_certificate', methods=('GET', 'POST'))
def team_form_volunteer_certificate(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(team['pid'])
    if not project:
        return redirect('/')

    is_ok_submit = False
    user = User(uid=g.user['account']['_id']).get()
    if 'profile_real' in user:
        _check = []
        for k in ('name', 'roc_id', 'birthday', 'company'):
            if k in user['profile_real'] and user['profile_real'][k]:
                _check.append(True)
            else:
                _check.append(False)

        is_ok_submit = all(_check)

    if request.method == 'GET':
        return render_template('./form_volunteer_certificate.html', project=project, team=team, is_ok_submit=is_ok_submit)

    elif request.method == 'POST':
        if not is_ok_submit:
            return u'', 406

        return u'%s' % request.form

@VIEW_TEAM.route('/<pid>/<tid>/form/appreciation', methods=('GET', 'POST'))
def team_form_appreciation(pid, tid):
    team = Team.get(pid, tid)
    if not team:
        return redirect('/')

    project = Project.get(team['pid'])
    if not project:
        return redirect('/')

    if request.method == 'GET':
        names = {
            'oauth': g.user['data']['name'],
        }

        if 'profile' in g.user['account'] and \
           'badge_name' in g.user['account']['profile'] and \
           g.user['account']['profile']['badge_name']:
            names['badge_name'] = g.user['account']['profile']['badge_name']

        if 'profile_real' in g.user['account'] and \
           'name' in g.user['account']['profile_real'] and \
           g.user['account']['profile_real']['name']:
            names['real_name'] = g.user['account']['profile_real']['name']

        select_value = 'no'
        form_data = Form.get_appreciation(pid=pid, uid=g.user['account']['_id'])
        if form_data and 'data' in form_data and 'key' in form_data['data']:
            if 'available' in form_data['data'] and form_data['data']['available']:
                select_value = form_data['data']['key']

        return render_template('./form_appreciation.html',
            project=project, team=team, names=names.items(), select_value=select_value)

    elif request.method == 'POST':
        if request.form['volunteer_certificate'] not in ('oauth', 'badge_name', 'real_name', 'no'):
            return u'', 406

        if request.form['volunteer_certificate'] == 'no':
            data = {'available': False}

        else:
            if request.form['volunteer_certificate'] == 'oauth':
                name = g.user['data']['name']
            elif request.form['volunteer_certificate'] == 'badge_name':
                name = g.user['account']['profile']['badge_name']
            elif request.form['volunteer_certificate'] == 'real_name':
                name = g.user['account']['profile_real']['name']

            data = {
                'available': True,
                'key': request.form['volunteer_certificate'],
                'value': name,
            }

        Form().update_appreciation(pid=team['pid'], uid=g.user['account']['_id'], data=data)
        return redirect(url_for('team.team_form_appreciation', pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))
