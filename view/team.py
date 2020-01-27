import html

from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markdown import markdown

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

        return render_template('./team_edit_user.html', project=project, team=team, waitting_list=waitting_list)

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
