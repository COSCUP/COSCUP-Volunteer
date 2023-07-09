''' Team '''
# pylint: disable=too-many-lines
import csv
import html
import io
import json
import re
from random import choice
from typing import Any, Callable

import arrow
import phonenumbers
from bson.objectid import ObjectId
from flask import (Blueprint, flash, g, jsonify, make_response, redirect,
                   render_template, request, url_for)
from flask.wrappers import Response
from markdown import markdown
from pydantic import BaseModel, Field
from werkzeug.wrappers import Response as ResponseBase

import setting
from celery_task.task_applyreview import applyreview_submit_one
from celery_task.task_expense import expense_create
from models.teamdb import TeamMemberChangedDB, TeamPlanDB
from module.applyreview import ApplyReview
from module.budget import Budget
from module.dispense import Dispense
from module.expense import Expense
from module.form import Form, FormAccommodation, FormTrafficFeeMapping
from module.mattermost_bot import MattermostTools
from module.team import Team
from module.users import AccountPass, User
from module.waitlist import WaitList
from structs.teams import TeamUsers
from view.utils import check_the_team_and_project_are_existed

VIEW_TEAM = Blueprint('team', __name__, url_prefix='/team')


@VIEW_TEAM.route('/<pid>/<tid>/')
def index(pid: str, tid: str) -> str | ResponseBase:
    ''' Index page '''
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    for k in ('desc', 'public_desc'):
        if k not in team.__dict__ or not team.__dict__[k]:
            team.__dict__[k] = ''
        else:
            team.__dict__[k] = re.sub('<a href="javascript:.*"',
                                      '<a href="/"', markdown(html.escape(team.__dict__[k])))

    preview_public = False
    if 'preview' in request.args:
        preview_public = True

    teamusers = TeamUsers.parse_obj(team)
    join_able = not (g.user['account']['_id'] in teamusers.members or
                     g.user['account']['_id'] in teamusers.chiefs or
                     g.user['account']['_id'] in teamusers.owners or
                     g.user['account']['_id'] in project.owners)

    is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                g.user['account']['_id'] in teamusers.owners or
                g.user['account']['_id'] in project.owners)

    return render_template('./team_index.html', team=team.dict(by_alias=True),
                           project=project.dict(by_alias=True),
                           join_able=join_able, is_admin=is_admin,
                           preview_public=preview_public)


@VIEW_TEAM.route('/<pid>/<tid>/calendar')
def calendar(pid: str, tid: str) -> str | ResponseBase:
    ''' calendar '''
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    if project.calendar:
        teamusers = TeamUsers.parse_obj(team)
        is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                    g.user['account']['_id'] in teamusers.owners or
                    g.user['account']['_id'] in project.owners)

        return render_template('./team_calendar.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True), is_admin=is_admin)

    return redirect(url_for('team.index',
                            pid=team.pid, tid=team.id, _scheme='https', _external=True))


class UserInfoBase(BaseModel):
    ''' UserInfoBase '''
    id: str = Field(alias='_id')
    profile: dict[str, str]
    oauth: dict[str, str]
    is_chief: bool = Field(default=False)
    chat: dict[str, str] | None = Field(default_factory=dict)


@VIEW_TEAM.route('/<pid>/<tid>/members', methods=('GET', 'POST'))
def members(pid: str, tid: str) -> str | ResponseBase:  # pylint: disable=too-many-branches
    ''' members '''
    # pylint: disable=too-many-locals
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                g.user['account']['_id'] in teamusers.owners or
                g.user['account']['_id'] in project.owners)

    if request.method == 'GET':
        return render_template('./team_members.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True), is_admin=is_admin)

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            list_teams = []
            if 'tid' in post_data and post_data['tid'] != tid:
                team = Team.get(pid=pid, tid=post_data['tid'])
                if team is None:
                    raise Exception('Not found')

            else:
                for lteam in Team.list_by_pid(pid=pid):
                    list_teams.append(
                        {'_id': lteam.id, 'name': lteam.name})

            uids = []
            if team.chiefs:
                uids.extend(team.chiefs)
            if team.members:
                uids.extend(team.members)

            uids = list(set(uids))
            users_info = User.get_info(uids=uids)

            result_members = []
            for uid in uids:
                if uid in users_info:
                    user = UserInfoBase.parse_obj(
                        {'_id': uid,
                         'profile': {'badge_name': users_info[uid]['profile']['badge_name']},
                         'oauth': {'picture': users_info[uid]['oauth']['picture']}})

                    if team.chiefs and uid in team.chiefs:
                        user.is_chief = True

                    mid = MattermostTools.find_possible_mid(uid=uid)
                    if mid:
                        user.chat = {
                            'mid': mid, 'name': MattermostTools.find_user_name(mid=mid)}

                    result_members.append(user.dict(by_alias=True))

            call_func_bg: Callable[[dict[str, Any], ],
                                   Any] = lambda u: u['profile']['badge_name'].lower()
            result_members.sort(key=call_func_bg)

            call_func_chief: Callable[[
                dict[str, Any], ], Any] = lambda u: u['is_chief']
            result_members.sort(key=call_func_chief, reverse=True)

            tags = []
            if team.tag_members:
                tags = [t_m.dict() for t_m in team.tag_members]

            members_tags = Team.get_members_tags(pid=team.pid, tid=team.id)

            return jsonify({'members': result_members, 'teams': list_teams,
                            'tags': tags, 'members_tags': members_tags})

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/edit', methods=('GET', 'POST'))
def team_edit(pid: str, tid: str) -> str | ResponseBase:
    ''' Team edit '''
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                g.user['account']['_id'] in teamusers.owners or
                g.user['account']['_id'] in project.owners)

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        return render_template('./team_edit_setting.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True))

    if request.method == 'POST':
        data = {
            'name': request.form['name'].strip(),
            'public_desc': request.form['public_desc'].strip(),
            'desc': request.form['desc'].strip(),
        }
        Team.update_setting(pid=team.pid, tid=team.id, data=data)
        return redirect(url_for('team.team_edit',
                                pid=team.pid, tid=team.id, _scheme='https', _external=True))

    return Response('', status=404)


@VIEW_TEAM.route('/<pid>/<tid>/edit_user/dl_waiting', methods=('GET',))
def team_edit_user_dl_waiting(pid: str, tid: str) -> str | ResponseBase:
    ''' Team edit user '''
    # pylint: disable=too-many-locals
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                g.user['account']['_id'] in teamusers.owners or
                g.user['account']['_id'] in project.owners)

    if not is_admin:
        return redirect('/')

    waitting_list: list[dict[str, Any]] = []
    waiting_data = WaitList.list_by_team(pid=pid, tid=tid)

    if waiting_data is not None:
        for waiting in waiting_data:
            waitting_list.append(waiting)

    users_info = User.get_info([u['uid'] for u in waitting_list])

    result: dict[str, dict[str, str]] = {}
    for waiting in waitting_list:
        uid = waiting['uid']
        result[uid] = {}
        result[uid]['name'] = users_info[uid]['profile']['badge_name']
        email = users_info[uid]['oauth']['email']
        result[uid]['email_for_to'] = f'"{result[uid]["name"]}" <{email}>'
        result[uid]['submission'] = waiting['note']
        result[uid]['intro'] = users_info[uid]['profile']['intro'].replace(
            '\n', '\r\n')
        result[uid]['url'] = f'https://{setting.DOMAIN}/user/{uid}'
        result[uid]['date'] = arrow.get(ObjectId(waiting['_id']).generation_time).to(
            'Asia/Taipei').format('YYYY-MM-DD')

    with io.StringIO() as files:
        csv_writer = csv.DictWriter(files,
                                    fieldnames=['date', 'name', 'email_for_to', 'submission',
                                                'url', 'intro'],
                                    quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()
        csv_writer.writerows(result.values())

        filename = f"coscup_waiting_{pid}_{tid}_" + \
                   f"{arrow.now().to('Asia/Taipei').format('YYYYMMDD-HHmmss')}.csv"

        return Response(
            files.getvalue().encode(encoding="utf-8-sig"),
            mimetype='text/csv',
            headers={'Content-disposition': f'attachment; filename={filename}',
                     'x-filename': filename,
                     })


@VIEW_TEAM.route('/<pid>/<tid>/edit_user', methods=('GET', 'POST'))
def team_edit_user(pid: str, tid: str) -> str | ResponseBase:
    ''' Team edit user '''
    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                g.user['account']['_id'] in teamusers.owners or
                g.user['account']['_id'] in project.owners)

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        waitting_list: list[dict[str, Any]] = []
        waiting_data = WaitList.list_by_team(pid=pid, tid=tid)

        if waiting_data is not None:
            for waiting in waiting_data:
                waitting_list.append(waiting)

        uids = [u['uid'] for u in waitting_list]
        users_info = User.get_info(uids)

        waiting_uids: list[str] = []
        for user in waitting_list:
            user['_info'] = users_info[user['uid']]
            user['_history'] = []
            for wait_info in WaitList.find_history(pid=pid, uid=user['uid']):
                if 'result' not in wait_info:
                    wait_info['result'] = 'waitting'

                user['_history'].append(wait_info)

            user_data = User(uid=user['uid']).get()
            if user_data:
                user['_mail'] = user_data['mail']

            waiting_uids.append(user['uid'])

        apply_review_results: dict[str, Any] = {}
        waiting_uids_tags_name: dict[str, list[str]] = {}
        if waiting_uids:
            apply_review_results = ApplyReview.get(
                pid=pid, tid=tid, uids=waiting_uids)

            for item in apply_review_results.values():
                item['messages'] = [choice(item['messages']), ]
                for raw in item['messages']:
                    raw['content'] = markdown(
                        raw['content'].replace('\n\n', '\n'))

            waiting_uids_tags_data = Team.get_tags_by_uids(
                pid=pid, tid=tid, uids=waiting_uids)
            mapping_name: dict[str, str] = {
                tag.id: tag.name for tag in team.tag_members} if team.tag_members else {}
            for uid, tags_data in waiting_uids_tags_data.items():
                if uid not in waiting_uids_tags_name:
                    waiting_uids_tags_name[uid] = []

                for tag in tags_data:
                    waiting_uids_tags_name[uid].append(mapping_name[tag])

        return render_template('./team_edit_user.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(
                                   by_alias=True, exclude_none=True),
                               waitting_list=waitting_list,
                               waiting_uids_tags_name=waiting_uids_tags_name,
                               apply_review_results=apply_review_results,
                               )

    if request.method == 'POST':  # pylint: disable=too-many-return-statements, too-many-nested-blocks
        data = request.json

        if data and data['case'] == 'deluser':
            Team.update_members(pid=pid, tid=tid, del_uids=[data['uid'], ])
        elif data and data['case'] == 'history':
            history = []
            for raw in WaitList.find_history_in_team(uid=data['uid'], pid=pid, tid=tid):
                raw['_id'] = str(raw['_id'])
                history.append(raw)

            return jsonify({'history': history})
        elif data and data['case'] == 'members':
            result_members = []
            if team.members or team.chiefs:
                _all_uids = set(teamusers.members + teamusers.chiefs)

                users_info = User.get_info(list(_all_uids))
                for uid in _all_uids:
                    result_members.append(users_info[uid])

                for user in result_members:
                    user['chat'] = {}
                    mid = MattermostTools.find_possible_mid(uid=user['_id'])
                    if mid:
                        user['chat'] = {
                            'mid': mid, 'name': MattermostTools.find_user_name(mid=mid)}

                    user['phone'] = {'country_code': '', 'phone': ''}
                    if 'phone' in user['profile_real'] and user['profile_real']['phone']:
                        phone = phonenumbers.parse(
                            user['profile_real']['phone'])
                        if phone.country_code:
                            user['phone']['country_code'] = \
                                phonenumbers.COUNTRY_CODE_TO_REGION_CODE[
                                    phone.country_code][0]
                        user['phone']['phone'] = phonenumbers.format_number(
                            phone, phonenumbers.PhoneNumberFormat.NATIONAL)

                call_func_bg: Callable[[dict[str, Any], ],
                                       Any] = lambda u: u['profile']['badge_name'].lower()
                result_members = sorted(result_members, key=call_func_bg)

                return jsonify({
                    'members': result_members,
                    'tags': [t_m.dict() for t_m in team.tag_members] if team.tag_members else [],
                    'members_tags': Team.get_members_tags(pid=pid, tid=tid),
                })

        elif data and data['case'] == 'add_tag':
            result = Team.add_tag_member(
                pid=pid, tid=tid, tag_name=data['tag_name'])
            return jsonify({'tag': result})

        elif data and data['case'] == 'update_member_tags':
            team_tags = []
            if team.tag_members:
                for tag in team.tag_members:
                    team_tags.append(tag.id)

            team_members = set(teamusers.members + teamusers.chiefs)

            tag_datas = {}
            for uid in team_members:
                if uid in data['data']:
                    tag_datas[uid] = {'tags': list(
                        set(team_tags) & set(data['data'][uid]))}

            if tag_datas:
                Team.add_tags_to_members(pid=pid, tid=tid, data=tag_datas)

            return jsonify({'data': tag_datas})

        elif data and data['case'] == 'del_tag':
            Team.del_tag(pid=pid, tid=tid, tag_id=data['tag']['id'])

    return jsonify({})


@VIEW_TEAM.route('/<pid>/<tid>/edit_user/api', methods=('GET', 'POST'))
def team_edit_user_api(pid: str, tid: str) -> ResponseBase:  # pylint: disable=too-many-branches
    ''' Team edit user API '''
    # pylint: disable=too-many-return-statements, too-many-locals
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    is_admin = (g.user['account']['_id'] in teamusers.chiefs or
                g.user['account']['_id'] in teamusers.owners or
                g.user['account']['_id'] in project.owners)

    if not is_admin:
        return redirect('/')

    if request.method == 'GET':
        if request.args['casename'] == 'join':
            user = User(uid=request.args['uid']).get()
            if user is not None:
                user_waitting_data = WaitList.list_by_team(
                    pid=pid, tid=tid, uid=user['_id'])
                if not user_waitting_data:
                    return jsonify({})

                for user_waitting in user_waitting_data:
                    users_info = User.get_info([user['_id'], ])
                    if users_info:
                        user_data = {
                            'badge_name': users_info[user['_id']]['profile']['badge_name'],
                            'picture': users_info[user['_id']]['oauth']['picture'],
                            'uid': user['_id'],
                            'note': user_waitting['note'],
                            'wid': f"{user_waitting['_id']}",
                        }

                        return jsonify(user_data)

        return jsonify({})

    if request.method == 'POST':
        data = request.json
        if not data:
            return make_response({}, 404)

        if data['casename'] == 'join':
            if data['result'] == 'approval':
                all_members = len(set(teamusers.members + teamusers.chiefs))
                if team.headcount is not None and \
                        team.headcount > 0 and all_members >= team.headcount:

                    return Response(
                        response=json.dumps({
                            'status': 'fail',
                            'message': 'over headcount.'}),
                        status=406,
                        mimetype='application/json',
                    )

            wait_info = WaitList.make_result(
                wid=data['wid'], pid=pid, uid=data['uid'], result=data['result'])
            if wait_info and 'result' in wait_info:
                if wait_info['result'] == 'approval':
                    Team.update_members(
                        pid=pid, tid=tid, add_uids=[data['uid'], ])
                elif wait_info['result'] == 'deny':
                    TeamMemberChangedDB().make_record(
                        pid=pid, tid=tid, action={'deny': [data['uid'], ]})

            return jsonify({'status': 'ok'})

        if data['casename'] == 'get_tags':
            return jsonify({
                'user_tags': Team.get_tags_by_uids(pid=pid, tid=tid, uids=[data['uid'], ]),
                'tags': [raw.dict() for raw in team.tag_members] if team.tag_members else [],
            })

        if data['casename'] == 'presave_tags':
            team_tags = []
            if team.tag_members:
                for tag in team.tag_members:
                    team_tags.append(tag.id)

            tag_datas: dict[str, dict[str, list[str]]] = {}
            tag_datas[data['uid']] = {'tags': list(
                set(team_tags) & set(data['tags'] or []))}
            if tag_datas:
                Team.add_tags_to_members(pid=pid, tid=tid, data=tag_datas)
            return jsonify({
                'user_tags': data['tags'],
            })

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/join_to', methods=('GET', 'POST'))
def team_join_to(pid: str, tid: str) -> str | ResponseBase:  # pylint: disable=too-many-return-statements,too-many-branches
    ''' Team join to '''
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if g.user['account']['_id'] in teamusers.members or \
            g.user['account']['_id'] in teamusers.chiefs:
        return redirect(url_for('team.index', pid=pid, tid=tid))

    user_pass = AccountPass(uid=g.user['account']['_id'])

    if user_pass.is_edu_account:
        flash('請勿使用學校帳號註冊！')

    if not user_pass.is_profile:
        flash('''請完成「<a href="/setting/profile">我的簡介</a>」，
        編寫內容請包含：<strong>自我介紹</strong>、<strong>技能</strong>、<strong>年度期待</strong>
        （參考：<a href="/user/e161787f">範例一</a>、
        <a href="/user/2b17b7b8">範例二</a>、<a href="/user/6c74e623">範例三</a>）。
        可使用 Markdown 的語法排版（<a href="https://markdown.tw/">語法參考</a>）。''')

    if not user_pass.is_coc:
        flash('請先閱讀「<a href="/coc">社群守則</a>」。')

    if not user_pass.is_security_guard:
        flash('請先閱讀「<a href="/security_guard">資料保護原則 </a>」。')

    if not user_pass.has_chat:
        flash(
            '請先建立 Mattermost 帳號，前往「<a href="/setting/link/chat">連結 chat.coscup.org 帳號</a>」。')

    if request.method == 'GET':
        is_in_wait = WaitList.is_in_wait(
            pid=team.pid, tid=team.id, uid=g.user['account']['_id'])

        if not is_in_wait and team.public_desc is not None:
            team.public_desc = re.sub('<a href="javascript:.*"', '<a href="/"',
                                      markdown(html.escape(team.public_desc)))

        return render_template('./team_join_to.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True), is_in_wait=is_in_wait)

    if request.method == 'POST':
        if not all((user_pass.is_profile, user_pass.is_coc, user_pass.is_security_guard)):
            return redirect(f'/team/{team.pid}/{team.id}/join_to')

        note: str = request.form['note'].strip()

        if len(note) < 100:
            flash('請重新整理此頁面後再次填寫申請加入。')
            return redirect(f'/team/{team.pid}/{team.id}/join_to')

        WaitList.join_to(
            pid=pid, tid=tid, uid=g.user['account']['_id'], note=note)
        TeamMemberChangedDB().make_record(
            pid=pid, tid=tid, action={'waiting': [g.user['account']['_id'], ]})
        applyreview_submit_one.apply_async(kwargs={
            'pid': pid, 'tid': tid, 'uid': g.user['account']['_id'],
        })

        return redirect(f'/team/{team.pid}/{team.id}/join_to')

    return Response('', status=404)


@VIEW_TEAM.route('/<pid>/<tid>/form/api', methods=('GET', 'POST'))
def team_form_api(pid: str, tid: str) -> ResponseBase:
    ''' Team form API '''
    team, _, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'GET':
        if request.args['case'] == 'traffic_fee':
            data = FormTrafficFeeMapping.get(pid=pid)
            if data is not None:
                return jsonify({'locations': [(item.location, item.fee) for item in data]})

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/form/accommodation', methods=('GET', 'POST'))
def team_form_accommodation(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form accommodation '''
    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    is_ok_submit = False
    user = g.user['account']
    if 'profile_real' in user and 'name' in user['profile_real'] and \
            'roc_id' in user['profile_real'] and 'phone' in user['profile_real']:
        if user['profile_real']['name'] and user['profile_real']['roc_id'] and \
                user['profile_real']['phone']:
            is_ok_submit = True

    if request.method == 'GET':
        return render_template('./form_accommodation.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True),
                               is_ok_submit=is_ok_submit)

    if request.method == 'POST':
        if not is_ok_submit:
            return Response('', status=406)

        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            raw = {'selected': 'no', 'mixed': True}
            room = {}

            form_data = Form.get_accommodation(
                pid=pid, uid=g.user['account']['_id'])
            if form_data:
                raw['selected'] = form_data['data']['key']
                raw['mixed'] = form_data['data']['mixed']

                if 'room' in form_data['data'] and form_data['data']['room']:
                    room['no'] = form_data['data']['room']
                    room['key'] = form_data['data']['room_key']
                    room['exkey'] = form_data['data'].get('room_exkey', '')

                    room['mate'] = {}
                    _user_room, mate_room = FormAccommodation.get_room_mate(
                        pid=pid, uid=g.user['account']['_id'])
                    if mate_room:
                        user_info = User.get_info(uids=[mate_room['uid'], ])[
                            mate_room['uid']]
                        room['mate'] = {
                            'uid': mate_room['uid'],
                            'name': user_info['profile']['badge_name'],
                            'tid': '',
                            'picture': user_info['oauth']['picture'],
                        }

            return jsonify({'data': raw, 'room': room})

        if post_data and post_data['casename'] == 'update':
            if not project.formswitch.accommodation:
                return make_response({}, 401)

            selected = html.escape(post_data['selected'])

            if selected not in ('no', 'yes', 'yes-longtraffic'):
                return Response('', status=406)

            data = {
                'status': selected in ('yes', 'yes-longtraffic'),
                'key': selected,
                'mixed': post_data['mixed']
            }

            Form.update_accommodation(
                pid=pid, uid=g.user['account']['_id'], data=data)

            return jsonify({'data': {'selected': selected}})

        if post_data and post_data['casename'] == 'makechange':
            return jsonify({'msg': '今年不適用！'})

    return jsonify({})


class FeeMapping(BaseModel):
    ''' FeeMapping '''
    fee: int
    howto: str
    apply: str
    fromwhere: str


@VIEW_TEAM.route('/<pid>/<tid>/form/traffic_fee', methods=('GET', 'POST'))
def team_form_traffic_fee(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form traffic fee '''
    # pylint: disable=too-many-branches,too-many-return-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    is_ok_submit = False
    user = g.user['account']
    feemapping = FormTrafficFeeMapping.get(pid=pid)

    if project.traffic_fee_doc == 'https://on.org/' and feemapping:
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
        return render_template('./form_traffic_fee.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True),
                               data=data, is_ok_submit=is_ok_submit)

    if request.method == 'POST':
        if not project.formswitch.traffic:
            return Response('', status=401)

        if is_ok_submit and feemapping and \
                request.form['fromwhere'] in [item.location for item in feemapping]:
            fee_data: FeeMapping = FeeMapping.parse_obj({
                'fee': int(request.form['fee']),
                'howto': request.form['howto'].strip(),
                'apply': request.form['apply'].strip() == 'yes',
                'fromwhere': request.form['fromwhere'],
            })
            Form.update_traffic_fee(
                pid=pid, uid=g.user['account']['_id'], data=fee_data.dict())
            return redirect(url_for('team.team_form_traffic_fee',
                                    pid=team.pid, tid=team.id,
                                    _scheme='https', _external=True))

        return Response('', status=406)

    return Response('', status=404)


@VIEW_TEAM.route('/<pid>/<tid>/form/volunteer_certificate', methods=('GET', 'POST'))
def team_form_volunteer_certificate(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form volunteer certificate '''
    # pylint: disable=too-many-return-statements,too-many-branches
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
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
        form_data = Form.get_volunteer_certificate(
            pid=pid, uid=g.user['account']['_id'])
        if form_data and 'data' in form_data and 'value' in form_data['data']:
            select_value = 'yes' if form_data['data']['value'] else 'no'
        else:
            select_value = 'no'

        return render_template('./form_volunteer_certificate.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True),
                               is_ok_submit=is_ok_submit, select_value=select_value)

    if request.method == 'POST':
        if not project.formswitch.certificate:
            return Response('', status=401)

        if not is_ok_submit:
            return Response('', status=406)

        data = {'value': request.form['volunteer_certificate'] == 'yes'}
        Form.update_volunteer_certificate(
            pid=team.pid, uid=g.user['account']['_id'], data=data)

        return redirect(url_for('team.team_form_volunteer_certificate',
                                pid=team.pid, tid=team.id, _scheme='https', _external=True))

    return make_response({}, 404)


class AppreciationData(BaseModel):
    ''' AppreciationData '''
    available: bool = Field(default=False)
    key: str = Field(default='')
    value: str = Field(default='')


@VIEW_TEAM.route('/<pid>/<tid>/form/appreciation', methods=('GET', 'POST'))
def team_form_appreciation(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form appreciation '''
    # pylint: disable=too-many-branches,too-many-return-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
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
        form_data = Form.get_appreciation(
            pid=pid, uid=g.user['account']['_id'])
        if form_data and 'data' in form_data and 'key' in form_data['data']:
            if 'available' in form_data['data'] and form_data['data']['available']:
                select_value = form_data['data']['key']

        return render_template('./form_appreciation.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True), names=names.items(),
                               select_value=select_value)

    if request.method == 'POST':
        if not project.formswitch.appreciation:
            return Response('', status=401)

        if request.form['appreciation'] not in ('oauth', 'badge_name', 'real_name', 'no'):
            return Response('', status=406)

        if request.form['appreciation'] == 'no':
            app_data = AppreciationData()

        else:
            if request.form['appreciation'] == 'oauth':
                name = g.user['data']['name']
            elif request.form['appreciation'] == 'badge_name':
                name = g.user['account']['profile']['badge_name']
            elif request.form['appreciation'] == 'real_name':
                name = g.user['account']['profile_real']['name']
            else:
                raise NameError("Can not find the `name`.")

            app_data = AppreciationData.parse_obj({
                'available': True,
                'key': request.form['appreciation'],
                'value': name,
            })

        Form().update_appreciation(
            pid=team.pid, uid=g.user['account']['_id'], data=app_data.dict())

        return redirect(url_for('team.team_form_appreciation',
                                pid=team.pid, tid=team.id, _scheme='https', _external=True))

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/form/clothes', methods=('GET', 'POST'))
def team_form_clothes(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form clothes '''
    # pylint: disable=too-many-return-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_clothes.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            data = Form.get_clothes(
                pid=team.pid, uid=g.user['account']['_id'])

            htg = ''
            if not data:
                data = {'data': {'clothes': '',
                                 'htg': htg, }}

            if 'htg' in data['data']:
                htg = data['data']['htg']

            return jsonify({
                'clothes': data['data']['clothes'],
                'htg': htg,
            })

        if post_data and post_data['casename'] == 'post':
            if not project.formswitch.clothes:
                return make_response({}, 401)

            if 'clothes' in post_data and post_data['clothes']:
                Form.update_clothes(pid=team.pid, uid=g.user['account']['_id'],
                                    data={'clothes': post_data['clothes'],
                                          'htg': post_data['htg'],
                                          })
                return jsonify({})

    return jsonify({})


@VIEW_TEAM.route('/<pid>/<tid>/form/drink', methods=('GET', 'POST'))
def team_form_drink(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form drink '''
    # pylint: disable=too-many-return-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_drink.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()
        if post_data and post_data['casename'] == 'get':
            data = Form.get_drink(
                pid=team.pid, uid=g.user['account']['_id'])
            if not data:
                data = {'data': {'y18': False}}

            return jsonify({'data': data['data']})

        if post_data and post_data['casename'] == 'post':
            if 'y18' in post_data:
                data = {'y18': bool(post_data['y18'])}
                Form.update_drink(
                    pid=team.pid, uid=g.user['account']['_id'], data=data)

        return jsonify({})

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/form/parking_card', methods=('GET', 'POST'))
def team_form_parking_card(pid: str, tid: str) -> str | ResponseBase:
    ''' Team form parking card '''
    # pylint: disable=too-many-return-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'GET':
        return render_template('./form_parking_card.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True))

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            data = Form.get_parking_card(
                pid=team.pid, uid=g.user['account']['_id'])

            if not data:
                return jsonify({'data': {'carno': '', 'dates': []},
                                'parking_card_options': []})

            return jsonify({'data': data['data'],
                            'parking_card_options': []})

        if post_data and post_data['casename'] == 'post':
            if 'data' in post_data and post_data['data']:
                carno = post_data['data']['carno'].strip().upper()
                if not carno:
                    return jsonify({})

                dates = post_data['data']['dates']

                Form.update_parking_card(pid=team.pid, uid=g.user['account']['_id'],
                                         data={'carno': carno, 'dates': dates})

                return jsonify({})

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/plan/edit', methods=('GET', 'POST'))
def team_plan_edit(pid: str, tid: str) -> str | ResponseBase:
    ''' Team plan edit '''
    # pylint: disable=too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    is_admin: bool = (g.user['account']['_id'] in teamusers.chiefs or
                      g.user['account']['_id'] in teamusers.owners or
                      g.user['account']['_id'] in project.owners)

    if request.method == 'GET':
        return render_template('./team_plan_edit.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True), is_admin=is_admin)

    if request.method == 'POST':  # pylint: disable=too-many-nested-blocks
        data = request.get_json()
        if not data:
            return make_response({}, 404)

        today = arrow.now().format('YYYY-MM-DD')
        default = {'title': '', 'desc': '', 'start': today, 'end': '',
                   'tid': team.id, 'team_name': team.name, 'start_timestamp': 0}

        team_plan_db = TeamPlanDB()
        if 'case' in data and data['case'] == 'get':
            plan_data = team_plan_db.find_one({'pid': pid, 'tid': tid})
            if not plan_data:
                plan_data = {'data': [default, ]}

            if not plan_data['data']:
                plan_data['data'] = [default, ]

            for raw in plan_data['data']:
                raw['tid'] = tid
                raw['team_name'] = team.name

            others = []
            if 'import_others' in data and data['import_others']:
                for team_plan in team_plan_db.find({'pid': pid, 'tid': {'$nin': [tid, ]}}):
                    team_info = Team.get(pid=pid, tid=team_plan['tid'])

                    if not team_info:
                        continue

                    for raw in team_plan['data']:
                        raw['tid'] = tid
                        raw['team_name'] = team_info.name

                        others.append(raw)

            return jsonify({'data': plan_data['data'], 'default': default, 'others': others})

        if 'case' in data and data['case'] == 'get_schedular':
            query = {'pid': pid}
            if not data['import_others']:
                query['tid'] = tid

            dates: dict[str, list[dict[str, str]]] = {}
            for raw in team_plan_db.find(query):
                for plan in raw['data']:
                    if not plan['end']:
                        if plan['start'] not in dates:
                            dates[plan['start']] = []

                        dates[plan['start']].append(plan)
                    else:
                        for date in arrow.Arrow.range('day',
                                                      arrow.get(plan['start']),
                                                      arrow.get(plan['end'])):
                            d_format = date.format('YYYY-MM-DD')
                            if d_format not in dates:
                                dates[d_format] = []
                            dates[d_format].append(plan)

            return jsonify({'data': list(dates.items())})

        if 'case' in data and data['case'] == 'post':
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
                result = team_plan_db.add(pid=pid, tid=tid, data=_data)

                for raw in result['data']:
                    raw['tid'] = tid
                    raw['team_name'] = team.name
                    raw['start_timestamp'] = arrow.get(
                        raw['start']).timestamp()

                if not result['data']:
                    result['data'] = [default, ]

                others = []
                if 'import_others' in data and data['import_others']:
                    for team_plan in team_plan_db.find({'pid': pid, 'tid': {'$nin': [tid, ]}}):
                        team_info = Team.get(pid=pid, tid=team_plan['tid'])

                        if not team_info:
                            continue

                        for raw in team_plan['data']:
                            raw['tid'] = tid
                            raw['team_name'] = team_info.name
                            raw['start_timestamp'] = arrow.get(
                                raw['start']).timestamp()

                            others.append(raw)

                return jsonify({'data': result['data'], 'default': default, 'others': others})

        return jsonify({'data': [], 'default': default})

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/expense/', methods=('GET', 'POST'))
def team_expense_index(pid: str, tid: str) -> ResponseBase:
    ''' Team expense index '''
    # pylint: disable=too-many-return-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'POST':
        data = request.get_json()

        if data and data['casename'] == 'get':
            teams = []
            for _team in Team.list_by_pid(pid=project.id):
                teams.append({'name': _team.name, 'tid': _team.id})

            if html.escape(data['select_team']) in [_team['tid'] for _team in teams]:
                select_team = html.escape(data['select_team'])
            else:
                select_team = team.id

            items = []
            for item in Budget.get_by_tid(pid=pid, tid=select_team, only_enable=True):
                items.append(item)

            bank = User.get_bank(uid=g.user['account']['_id'])

            return jsonify({'teams': teams, 'items': items,
                            'select_team': select_team, 'bank': bank.dict()})

        if data and data['casename'] == 'add_expense':
            # create expense and send notification.
            expense = Expense.process_and_add(
                pid=project.id, tid=team.id, uid=g.user['account']['_id'], data=data)
            expense_create.apply_async(kwargs={'expense': expense})
            return jsonify({})

        if data and data['casename'] == 'get_has_sent':
            data = Expense.get_has_sent(
                pid=project.id, budget_id=data['buid'])
            return jsonify({'data': list(data)})

    return make_response({}, 404)


@VIEW_TEAM.route('/<pid>/<tid>/expense/lists', methods=('GET', 'POST'))
def team_expense_lists(pid: str, tid: str) -> str | ResponseBase:
    ''' Team expense lists '''
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'GET':
        budget_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
        return render_template('./expense_lists.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True),
                               budget_menu=budget_admin)

    return Response('', status=404)


@VIEW_TEAM.route('/<pid>/<tid>/expense/my', methods=('GET', 'POST'))
def team_expense_my(pid: str, tid: str) -> str | ResponseBase:
    ''' Team expense my '''
    # pylint: disable=too-many-locals,too-many-branches,too-many-return-statements,too-many-statements
    team, project, _redirect = check_the_team_and_project_are_existed(
        pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if not team or not project:
        return redirect('/')

    teamusers = TeamUsers.parse_obj(team)
    if not (g.user['account']['_id'] in teamusers.members or
            g.user['account']['_id'] in teamusers.chiefs):
        return redirect('/')

    if request.method == 'GET':
        budget_admin = Budget.is_admin(pid=pid, uid=g.user['account']['_id'])
        return render_template('./expense_my.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True),
                               budget_menu=budget_admin)

    if request.method == 'POST':
        data = request.get_json()

        if data and data['casename'] == 'get':
            teams = []
            for _team in Team.list_by_pid(pid=project.id):
                teams.append({'name': _team.name, 'tid': _team.id})

            buids = set()
            uids = set()
            items = {}
            dispense_ids = set()
            dispenses = []

            for item in Expense.get_by_create_by(pid=pid, create_by=g.user['account']['_id']):
                items[item['_id']] = item
                dispense_ids.add(item['dispense_id'])

            dispense_ids_list = list(dispense_ids)

            for item in Expense.get_by_dispense_id(dispense_ids_list):
                items[item['_id']] = item

            for item in items.values():
                buids.add(item['request']['buid'])
                uids.add(item['create_by'])

            for dispense in Dispense.get_by_ids(dispense_ids_list):
                dispenses.append(dispense)

            budgets = {}
            if buids:
                for raw in Budget.get(buids=list(buids), pid=pid):
                    budgets[raw['_id']] = raw

            users = {}
            if uids:
                user_datas = User.get_info(uids=list(uids))
                for uid, value in user_datas.items():
                    users[uid] = {
                        'oauth': value['oauth'],
                        'profile': {'badge_name': value['profile']['badge_name']}, }

            return jsonify({
                'teams': teams,
                'items': list(items.values()),
                'dispenses': dispenses,
                'budgets': budgets,
                'users': users,
                'status': Expense.status(),
                'my': g.user['account']['_id']
            })

        if data and data['casename'] == 'update':
            invoices = {}
            status = ''
            for expense in Expense.get_by_eid(expense_id=data['eid']):
                status = expense['status']
                for invoice in expense['invoices']:
                    invoices[invoice['iv_id']] = invoice

            for invoice in data['invoices']:
                if invoice['iv_id'] in invoices:
                    if status in ('1', ):
                        invoices[invoice['iv_id']
                                 ]['total'] = invoice['total']

                    if status in ('1', '2', '3'):
                        invoices[invoice['iv_id']
                                 ]['status'] = invoice['status'].strip()
                        invoices[invoice['iv_id']
                                 ]['name'] = invoice['name'].strip()

            Expense.update_invoices(
                expense_id=data['eid'], invoices=list(invoices.values()))

            if status in ('1', ):
                Expense.update_bank(expense_id=data['eid'], bank=data['bank'])

            if status in ('1', '2', '3'):
                Expense.update_request(
                    expense_id=data['eid'], rdata=data['req'])

            return jsonify({})

        if data and data['casename'] == 'remove':
            status = ''
            for expense in Expense.get_by_eid(expense_id=data['eid']):
                status = expense['status']

            if status in ('1', ):
                Expense.update_enable(expense_id=data['eid'], enable=False)

            return jsonify({})

    return make_response({}, 404)
