import html
import json
import re
import logging

import arrow
import phonenumbers
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from markdown import markdown

import setting
from models.teamdb import TeamMemberChangedDB
from models.teamdb import TeamPlanDB
from module.budget import Budget
from module.expense import Expense
from module.form import Form
from module.form import FormAccommodation
from module.form import FormTrafficFeeMapping
from module.mattermost_bot import MattermostTools
from module.team import Team
from module.users import User
from module.waitlist import WaitList
from view.utils import check_the_team_and_project_are_existed

VIEW_TEAM = Blueprint('team', __name__, url_prefix='/team')


@VIEW_TEAM.route('/<pid>/<tid>/')
def index(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    for k in ('desc', 'public_desc'):
        if k not in team:
            team[k] = ''
        else:
            team[k] = re.sub('<a href="javascript:.*"', '<a href="/"', markdown(html.escape(team[k])))

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

@VIEW_TEAM.route('/<pid>/<tid>/calendar')
def calendar(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if 'calendar' in project and project['calendar']:
        is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                    g.user['account']['_id'] in team['owners'] or \
                    g.user['account']['_id'] in project['owners'])

        return render_template('./team_calendar.html', project=project, team=team, is_admin=is_admin)

    return redirect(url_for('team.index', pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))

@VIEW_TEAM.route('/<pid>/<tid>/members', methods=('GET', 'POST'))
def members(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if request.method == 'GET':
        return render_template('./team_members.html', project=project, team=team, is_admin=is_admin)

    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            list_teams = []
            if 'tid' in post_data and post_data['tid'] != tid:
                team = Team.get(pid=pid, tid=post_data['tid'])

            else:
                for lteam in Team.list_by_pid(pid=pid):
                    list_teams.append({'_id': lteam['tid'], 'name': lteam['name']})

            uids = []
            uids.extend(team['chiefs'])
            uids.extend(team['members'])

            uids = list(set(uids))
            users_info = User.get_info(uids=uids)

            members = []
            for uid in uids:
                if uid in users_info:
                    user = {'_id': uid,
                            'profile': {'badge_name': users_info[uid]['profile']['badge_name']},
                                        'oauth': {'picture': users_info[uid]['oauth']['picture']}}

                    user['is_chief'] = False
                    if uid in team['chiefs']:
                        user['is_chief'] = True

                    user['chat'] = {}
                    mid = MattermostTools.find_possible_mid(uid=uid)
                    if mid:
                        user['chat'] = {'mid': mid, 'name': MattermostTools.find_user_name(mid=mid)}

                    members.append(user)

            members = sorted(members, key=lambda u: u['profile']['badge_name'].lower())

            tags = []
            if 'tag_members' in team and team['tag_members']:
                tags = team['tag_members']

            members_tags = Team.get_members_tags(pid=team['pid'], tid=team['tid'])

        return jsonify({'members': members, 'teams':list_teams,
                        'tags': tags, 'members_tags': members_tags})


@VIEW_TEAM.route('/<pid>/<tid>/edit', methods=('GET', 'POST'))
def team_edit(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

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
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

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
            u['_history'] = []
            for w in WaitList.find_history(pid=pid, uid=u['uid']):
                if 'result' not in w:
                    w['result'] = 'waitting'

                u['_history'].append(w)

            u['_mail'] = User(uid=u['uid']).get()['mail']

        return render_template('./team_edit_user.html',
                project=project, team=team, waitting_list=waitting_list)

    elif request.method == 'POST':
        data = request.json

        if data['case'] == 'deluser':
            Team.update_members(pid=pid, tid=tid, del_uids=[data['uid'], ])
        elif data['case'] == 'history':
            history = []
            for raw in WaitList.find_history_in_team(uid=data['uid'], pid=pid, tid=tid):
                raw['_id'] = str(raw['_id'])
                history.append(raw)

            return jsonify({'history': history})
        elif data['case'] == 'members':
            members = []
            if team['members'] or team['chiefs']:
                _all_uids = set(team['chiefs']) | set(team['members'])
                users_info = User.get_info(list(_all_uids))
                for uid in _all_uids:
                    members.append(users_info[uid])

                for u in members:
                    u['chat'] = {}
                    mid = MattermostTools.find_possible_mid(uid=u['_id'])
                    if mid:
                        u['chat'] = {'mid': mid, 'name': MattermostTools.find_user_name(mid=mid)}

                    u['phone'] = {'country_code': '', 'phone': ''}
                    if 'phone' in u['profile_real'] and u['profile_real']['phone']:
                        phone = phonenumbers.parse(u['profile_real']['phone'])
                        u['phone']['country_code'] = phonenumbers.COUNTRY_CODE_TO_REGION_CODE[phone.country_code][0]
                        u['phone']['phone'] = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.NATIONAL)

                members = sorted(members, key=lambda u: u['profile']['badge_name'])

                return jsonify({
                        'members': members,
                        'tags': team.get('tag_members', []),
                        'members_tags': Team.get_members_tags(pid=pid, tid=tid),
                    })

        elif data['case'] == 'add_tag':
            result = Team.add_tag_member(pid=pid, tid=tid, tag_name=data['tag_name'])
            return jsonify({'tag': result})

        elif data['case'] == 'update_member_tags':
            team_tags = [i['id'] for i in team.get('tag_members', [])]
            team_members = set(team['members'] + team['chiefs'])

            tag_datas = {}
            for uid in team_members:
                if uid in data['data']:
                    tag_datas[uid] = {'tags': list(set(team_tags) & set(data['data'][uid]))}

            if tag_datas:
                Team.add_tags_to_members(pid=pid, tid=tid, data=tag_datas)

            return jsonify({'data': tag_datas})

        elif data['case'] == 'del_tag':
            Team.del_tag(pid=pid, tid=tid, tag_id=data['tag']['id'])

            return jsonify({})

        return jsonify(data)

@VIEW_TEAM.route('/<pid>/<tid>/edit_user/api', methods=('GET', 'POST'))
def team_edit_user_api(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

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
        if data['result'] == 'approval':
            all_members = len(team['members']) + len(team['chiefs'])
            if 'headcount' in team and team['headcount'] and all_members >= team['headcount']:
                return jsonify({'status': 'fail', 'message': 'over headcount.'}), 406

        w = WaitList.make_result(wid=data['wid'], pid=pid, uid=data['uid'], result=data['result'])
        if w and 'result' in w:
            if w['result'] == 'approval':
                Team.update_members(pid=pid, tid=tid, add_uids=[data['uid'], ])
            elif w['result'] == 'deny':
                TeamMemberChangedDB().make_record(pid=pid, tid=tid, deny_uids=(data['uid'], ))

        return jsonify({'status': 'ok'})

@VIEW_TEAM.route('/<pid>/<tid>/join_to', methods=('GET', 'POST'))
def team_join_to(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if g.user['account']['_id'] in team['members'] or g.user['account']['_id'] in team['chiefs']:
        return redirect(url_for('team.index', pid=pid, tid=tid))

    if request.method == 'GET':
        is_in_wait = WaitList.is_in_wait(pid=team['pid'], tid=team['tid'], uid=g.user['account']['_id'])

        if not is_in_wait and 'public_desc' in team:
            team['public_desc'] = re.sub('<a href="javascript:.*"', '<a href="/"',
                    markdown(html.escape(team['public_desc'])))

        return render_template('./team_join_to.html', project=project, team=team, is_in_wait=is_in_wait)

    elif request.method == 'POST':
        WaitList.join_to(pid=pid, tid=tid, uid=g.user['account']['_id'], note=request.form['note'].strip())
        TeamMemberChangedDB().make_record(pid=pid, tid=tid, waiting_uids=(g.user['account']['_id'], ))

        return redirect('/project/%s/' % pid)

@VIEW_TEAM.route('/<pid>/<tid>/form/api', methods=('GET', 'POST'))
def team_form_api(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    if request.method == 'GET':
        if request.args['case'] == 'traffic_fee':
            return jsonify({'locations': list(FormTrafficFeeMapping.get(pid=pid)['data'].items())})

        return jsonify(request.args)

@VIEW_TEAM.route('/<pid>/<tid>/form/accommodation', methods=('GET', 'POST'))
def team_form_accommodation(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    is_ok_submit = False
    user = g.user['account']
    if 'profile_real' in user and 'name' in user['profile_real'] and 'roc_id' in user['profile_real'] and 'phone' in user['profile_real']:
        if user['profile_real']['name'] and user['profile_real']['roc_id'] and user['profile_real']['phone']:
            is_ok_submit = True

    if request.method == 'GET':
        return render_template('./form_accommodation.html',
                project=project, team=team, is_ok_submit=is_ok_submit)

    elif request.method == 'POST':
        if not is_ok_submit:
            return u'', 406

        post_data = request.get_json()

        if post_data['casename'] == 'get':
            raw = {'selected': 'no'}
            room = {}

            form_data = Form.get_accommodation(pid=pid, uid=g.user['account']['_id'])
            if form_data:
                raw['selected'] = form_data['data']['key']

                if 'room' in form_data['data'] and form_data['data']['room']:
                    room['no'] = form_data['data']['room']
                    room['key'] = form_data['data']['room_key']
                    room['exkey'] = form_data['data'].get('room_exkey', '')

                    room['mate'] = {}
                    _user_room, mate_room = FormAccommodation.get_room_mate(pid=pid, uid=g.user['account']['_id'])
                    if mate_room:
                        user_info = User.get_info(uids=[mate_room['uid'], ])[mate_room['uid']]
                        room['mate'] = {
                            'uid': mate_room['uid'],
                            'name': user_info['profile']['badge_name'],
                            'tid': '',
                            'picture': user_info['oauth']['picture'],
                        }

            return jsonify({'data': raw, 'room': room})

        elif post_data['casename'] == 'update':
            if post_data['selected'] not in ('no', 'yes', 'yes-longtraffic'):
                return u'', 406

            data = {
                'status': True if post_data['selected'] in ('yes', 'yes-longtraffic') else False,
                'key': post_data['selected'],
            }

            Form.update_accommodation(pid=pid, uid=g.user['account']['_id'], data=data)

            return jsonify({'data': {'selected': post_data['selected']}})

        elif post_data['casename'] == 'makechange':
            msg = FormAccommodation.make_exchange(pid=pid, uid=g.user['account']['_id'], exkey=post_data['key'].strip())
            return jsonify({'data': post_data, 'msg': msg})

@VIEW_TEAM.route('/<pid>/<tid>/form/traffic_fee', methods=('GET', 'POST'))
def team_form_traffic_fee(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    is_ok_submit = False
    user = g.user['account']
    feemapping = FormTrafficFeeMapping.get(pid=pid)

    if 'traffic_fee_doc' in project and project['traffic_fee_doc'] and feemapping and 'data' in feemapping and feemapping['data']:
        if 'profile_real' in user and 'bank' in user['profile_real']:
            _short_check = []
            for k in ('name', 'branch', 'no', 'code'):
                if k in user['profile_real']['bank'] and user['profile_real']['bank'][k]:
                    _short_check.append(True)
                else:
                    _short_check.append(False)

            if all(_short_check):
                is_ok_submit = True

    if request.method == 'GET':
        form_data = Form.get_traffic_fee(pid=pid, uid=g.user['account']['_id'])
        data = ''
        if form_data:
            data = json.dumps({
                'apply': 'yes' if form_data['data']['apply'] else 'no',
                'fromwhere': form_data['data']['fromwhere'],
                'howto': form_data['data']['howto'],
                'fee': form_data['data']['fee'],
            })
        return render_template('./form_traffic_fee.html', project=project, team=team,
                data=data, is_ok_submit=is_ok_submit)

    elif request.method == 'POST':
        if is_ok_submit and request.form['fromwhere'] in feemapping['data']:
            data = {
                'fee': int(request.form['fee']),
                'howto': request.form['howto'].strip(),
                'apply': True if request.form['apply'].strip() == 'yes' else False,
                'fromwhere': request.form['fromwhere'],
            }
            Form.update_traffic_fee(pid=pid, uid=g.user['account']['_id'], data=data)
            return redirect(url_for('team.team_form_traffic_fee',
                    pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))

        return u'', 406

@VIEW_TEAM.route('/<pid>/<tid>/form/volunteer_certificate', methods=('GET', 'POST'))
def team_form_volunteer_certificate(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    is_ok_submit = False
    user = g.user['account']
    if 'profile_real' in user:
        _check = []
        for k in ('name', 'roc_id', 'birthday', 'company'):
            if k in user['profile_real'] and user['profile_real'][k]:
                _check.append(True)
            else:
                _check.append(False)

        is_ok_submit = all(_check)

    if request.method == 'GET':
        form_data = Form.get_volunteer_certificate(pid=pid, uid=g.user['account']['_id'])
        if form_data and 'data' in form_data and 'value' in form_data['data']:
            select_value = 'yes' if form_data['data']['value'] else 'no'
        else:
            select_value = 'no'

        return render_template('./form_volunteer_certificate.html',
                project=project, team=team, is_ok_submit=is_ok_submit, select_value=select_value)

    elif request.method == 'POST':
        if not is_ok_submit:
            return u'', 406

        data = {'value': True if request.form['volunteer_certificate'] == 'yes' else False}
        Form.update_volunteer_certificate(pid=team['pid'], uid=g.user['account']['_id'], data=data)

        return redirect(url_for('team.team_form_volunteer_certificate',
                pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))

@VIEW_TEAM.route('/<pid>/<tid>/form/appreciation', methods=('GET', 'POST'))
def team_form_appreciation(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
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
        if request.form['appreciation'] not in ('oauth', 'badge_name', 'real_name', 'no'):
            return u'', 406

        if request.form['appreciation'] == 'no':
            data = {'available': False}

        else:
            if request.form['appreciation'] == 'oauth':
                name = g.user['data']['name']
            elif request.form['appreciation'] == 'badge_name':
                name = g.user['account']['profile']['badge_name']
            elif request.form['appreciation'] == 'real_name':
                name = g.user['account']['profile_real']['name']

            data = {
                'available': True,
                'key': request.form['appreciation'],
                'value': name,
            }

        Form().update_appreciation(pid=team['pid'], uid=g.user['account']['_id'], data=data)
        return redirect(url_for('team.team_form_appreciation', pid=team['pid'], tid=team['tid'], _scheme='https', _external=True))

@VIEW_TEAM.route('/<pid>/<tid>/form/clothes', methods=('GET', 'POST'))
def team_form_clothes(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_clothes.html', project=project, team=team)

    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            data = Form.get_clothes(pid=team['pid'], uid=g.user['account']['_id'])
            if not data:
                data = {'data': {'clothes': ''}}

            return jsonify({'clothes': data['data']['clothes']})

        elif post_data['casename'] == 'post':
            if 'clothes' in post_data and post_data['clothes']:
                Form.update_clothes(pid=team['pid'], uid=g.user['account']['_id'], data={'clothes': post_data['clothes']})
                return jsonify({})

@VIEW_TEAM.route('/<pid>/<tid>/form/drink', methods=('GET', 'POST'))
def team_form_drink(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_drink.html', project=project, team=team)

    elif request.method == 'POST':
        post_data = request.get_json()
        if post_data['casename'] == 'get':
            data = Form.get_drink(pid=team['pid'], uid=g.user['account']['_id'])
            if not data:
                data = {'data': {'y18': False}}

            return jsonify({'data': data['data']})

        elif post_data['casename'] == 'post':
            if 'y18' in post_data:
                data = {'y18': bool(post_data['y18'])}
                Form.update_drink(pid=team['pid'], uid=g.user['account']['_id'], data=data)

        return jsonify({'data': post_data})

@VIEW_TEAM.route('/<pid>/<tid>/form/parking_card', methods=('GET', 'POST'))
def team_form_parking_card(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not (g.user['account']['_id'] in team['members'] or \
            g.user['account']['_id'] in team['chiefs']):
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_parking_card.html', project=project, team=team)

    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            data = Form.get_parking_card(pid=team['pid'], uid=g.user['account']['_id'])
            if not data:
                return jsonify({'data': {'carno': '', 'dates': []}})

            return jsonify({'data': data['data']})

        elif post_data['casename'] == 'post':
            if 'data' in post_data and post_data['data']:
                carno = post_data['data']['carno'].strip().upper()
                if not carno:
                    return jsonify({})

                dates = post_data['data']['dates']

                Form.update_parking_card(pid=team['pid'], uid=g.user['account']['_id'],
                        data={'carno': carno, 'dates': dates})

                return jsonify({})

@VIEW_TEAM.route('/<pid>/<tid>/plan/edit', methods=('GET', 'POST'))
def team_plan_edit(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if request.method == 'GET':
        return render_template('./team_plan_edit.html', project=project, team=team, is_admin=is_admin)

    elif request.method == 'POST':
        data = request.get_json()
        today = arrow.now().format('YYYY-MM-DD')
        default = {'title': '', 'desc': '', 'start': today, 'end': '', 'tid': tid, 'team_name': team['name'], 'start_timestamp': 0}

        team_plan_db = TeamPlanDB()
        if 'case' in data and data['case'] == 'get':
            plan_data = team_plan_db.find_one({'pid': pid, 'tid': tid})
            if not plan_data:
                plan_data = {'data': [default, ]}

            if not plan_data['data']:
                plan_data['data'] = [default, ]

            for raw in plan_data['data']:
                raw['tid'] = tid
                raw['team_name'] = team['name']

            others = []
            if 'import_others' in data and data['import_others']:
                for team_plan in team_plan_db.find({'pid': pid, 'tid': {'$nin': [tid, ]}}):
                    team_info = Team.get(pid=pid, tid=team_plan['tid'])

                    for raw in team_plan['data']:
                        raw['tid'] = tid
                        raw['team_name'] = team_info['name']

                        others.append(raw)

            return jsonify({'data': plan_data['data'], 'default': default, 'others': others})

        elif 'case' in data and data['case'] == 'get_schedular':
            query = {'pid': pid}
            if not data['import_others']:
                query['tid'] = tid

            dates = {}
            team_plan = list(team_plan_db.find(query))
            for raw in team_plan:
                for plan in raw['data']:
                    if not plan['end']:
                        if plan['start'] not in dates:
                            dates[plan['start']] = []

                        dates[plan['start']].append(plan)
                    else:
                        for d in arrow.Arrow.range('day', arrow.get(plan['start']), arrow.get(plan['end'])):
                            d_format = d.format('YYYY-MM-DD')
                            if d_format not in dates:
                                dates[d_format] = []
                            dates[d_format].append(plan)

            return jsonify({'data': list(dates.items())})

        elif 'case' in data and data['case'] == 'post':
            if 'data' in data:
                _data = []
                for raw in data['data']:
                    if raw['title'] and raw['start']:
                        try:
                            arrow.get(raw['start'])
                            _raw = {}
                            for k in ('title', 'start', 'end', 'desc'):
                                _raw[k] = raw[k]
                            _data.append(_raw)
                        except arrow.parser.ParserError:
                            continue

                _data = sorted(_data, key=lambda d: arrow.get(d['start']))
                result = team_plan_db.save(pid=pid, tid=tid, data=_data)

                for raw in result['data']:
                    raw['tid'] = tid
                    raw['team_name'] = team['name']
                    raw['start_timestamp'] = arrow.get(raw['start']).timestamp()

                if not result['data']:
                    result['data'] = [default, ]

                others = []
                if 'import_others' in data and data['import_others']:
                    for team_plan in team_plan_db.find({'pid': pid, 'tid': {'$nin': [tid, ]}}):
                        team_info = Team.get(pid=pid, tid=team_plan['tid'])

                        for raw in team_plan['data']:
                            raw['tid'] = tid
                            raw['team_name'] = team_info['name']
                            raw['start_timestamp'] = arrow.get(raw['start']).timestamp()

                            others.append(raw)

                return jsonify({'data': result['data'], 'default': default, 'others': others})

        return jsonify({'data': [], 'default': default})

@VIEW_TEAM.route('/<pid>/<tid>/expense/', methods=('GET', 'POST'))
def team_expense_index(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if not is_admin:
        return redirect('/')

    if request.method == 'POST':
        data = request.get_json()

        if data['casename'] == 'get':
            teams = []
            for _team in Team.list_by_pid(pid=project['_id']):
                teams.append({'name': _team['name'], 'tid': _team['tid']})

            select_team = data['select_team']
            if select_team == '':
                select_team = team['tid']

            items = []
            for item in Budget.get_by_tid(pid=pid, tid=select_team):
                if item['enabled']:
                    item['enabled'] = 'true'
                else:
                    item['enabled'] = 'false'

                items.append(item)

            bank = User.get_bank(uid=g.user['account']['_id'])

            return jsonify({'teams': teams, 'items': items, 'select_team': select_team, 'bank': bank})

        elif data['casename'] == 'add_expense':
            Expense.proess_and_add(pid=project['_id'], tid=team['tid'], uid=g.user['account']['_id'], data=data)
            return jsonify(data)

@VIEW_TEAM.route('/<pid>/<tid>/expense/lists', methods=('GET', 'POST'))
def team_expense_lists(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    is_admin = (g.user['account']['_id'] in team['chiefs'] or \
                g.user['account']['_id'] in team['owners'] or \
                g.user['account']['_id'] in project['owners'])

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./expense_lists.html', project=project, team=team)

