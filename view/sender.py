''' Sneder '''
import csv
import html
import io
import random

import arrow
from flask import (Blueprint, g, jsonify, make_response, redirect,
                   render_template, request)
from werkzeug.wrappers import Response as ResponseBase

from celery_task.task_sendermailer import sender_mailer_start
from module.sender import SenderCampaign, SenderLogs, SenderReceiver
from module.team import Team
from module.users import User
from structs.teams import TeamUsers
from view.utils import check_the_team_and_project_are_existed

VIEW_SENDER = Blueprint('sender', __name__, url_prefix='/sender')


@VIEW_SENDER.route('/<pid>/<tid>/', methods=('GET', 'POST'))
def index(pid: str, tid: str) -> str | ResponseBase:  # pylint: disable=too-many-return-statements
    ''' Index page '''
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

    # ..note::
    # 1. create campaign (campaign name) / list campaign
    # 2. write title, content(jinja2, markdown)
    # 3. pick up receiver
    # 4. send / send test

    if request.method == 'GET':
        return render_template('./sender.html')

    if request.method == 'POST':
        data = request.get_json()

        if data and 'casename' in data and data['casename'] == 'get':
            campaigns = list(SenderCampaign.get_list(
                pid=team.pid, tid=team.id))
            raw_users_info = User.get_info(
                uids=[c['created']['uid'] for c in campaigns])
            users_info = {}
            for uid, value in raw_users_info.items():
                users_info[uid] = {
                    'uid': uid, 'name': value['profile']['badge_name']}

            return jsonify({'campaigns': campaigns, 'users_info': users_info})

        if data and 'casename' in data and data['casename'] == 'create':
            resp = SenderCampaign.create(
                name=data['name'], pid=team.pid, tid=team.id, uid=g.user['account']['_id'])

            return jsonify({'cid': resp['_id']})

    return jsonify({})


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/', methods=('GET', 'POST'))
def campaign(pid: str, tid: str, cid: str) -> str | ResponseBase:
    ''' campaign '''
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

    campaign_data = SenderCampaign.get(cid=cid, pid=pid, tid=tid)

    return render_template('./sender_campaign_index.html',
                           campaign=campaign_data, team=team.dict(by_alias=True))


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/content', methods=('GET', 'POST'))
def campaign_content(pid: str, tid: str, cid: str) -> str | ResponseBase:  # pylint: disable=too-many-return-statements
    ''' Campaign content '''
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
        campaign_data = SenderCampaign.get(
            cid=cid, pid=team.pid, tid=team.id)

        return render_template('./sender_campaign_content.html',
                               campaign=campaign_data, team=team.dict(by_alias=True))

    if request.method == 'POST':
        data = request.get_json()

        if data and 'casename' in data and data['casename'] == 'get':
            campaign_data = SenderCampaign.get(
                cid=cid, pid=team.pid, tid=team.id)

            if campaign_data:
                return jsonify({'mail': campaign_data['mail']})

        if data and 'casename' in data and data['casename'] == 'save':
            resp = SenderCampaign.save_mail(
                cid=cid,
                subject=data['data']['subject'].strip(),
                content=data['data']['content'].strip(),
                preheader=data['data']['preheader'].strip(),
                layout=data['data']['layout'].strip(),
            )
            return jsonify({'mail': resp['mail']})

    return make_response({}, 404)


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/receiver', methods=('GET', 'POST'))
def campaign_receiver(pid: str, tid: str, cid: str) -> str | ResponseBase:
    ''' campaign receiver '''
    # pylint: disable=too-many-branches,too-many-locals,too-many-return-statements
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

    campaign_data = SenderCampaign.get(cid=cid, pid=team.pid, tid=team.id)
    if request.method == 'GET':
        return render_template('./sender_campaign_receiver.html',
                               campaign=campaign_data, team=team.dict(by_alias=True))

    if request.method == 'POST':  # pylint: disable=too-many-nested-blocks
        if request.is_json:
            data = request.get_json()

            if data and 'casename' in data and data['casename'] == 'getinit':
                teams = []
                for _team in Team.list_by_pid(pid=team.pid):
                    teams.append({'tid': _team.id, 'name': _team.name})

                team_w_tags = []
                if team.tag_members:
                    team_w_tags = [t_m.dict() for t_m in team.tag_members]

                sender_receiver = SenderReceiver.get(pid=team.pid, cid=cid)

                picktags = []
                if campaign_data and 'team_w_tags' in campaign_data['receiver'] and \
                        team.id in campaign_data['receiver']['team_w_tags']:
                    picktags = campaign_data['receiver']['team_w_tags'][team.id]

                if campaign_data:
                    return jsonify({'teams': teams,
                                    'team_w_tags': team_w_tags,
                                    'pickteams': campaign_data['receiver']['teams'],
                                    'picktags': picktags,
                                    'is_all_users': campaign_data['receiver']['all_users'],
                                    'all_users_count': User.count(),
                                    'filedata': sender_receiver,
                                    })

            if data and 'casename' in data and data['casename'] == 'save':
                tids = [team.id for team in Team.list_by_pid(pid=team.pid)]

                _result = []
                for tid_info in tids:
                    if tid_info in data['pickteams']:
                        _result.append(tid_info)

                _team_w_tags = []
                if team.tag_members:
                    for tag in team.tag_members:
                        if tag.id in data['picktags']:
                            _team_w_tags.append(tag.id)

                return jsonify(SenderCampaign.save_receiver(
                    cid=cid, teams=_result, team_w_tags={
                        team.id: _team_w_tags},
                    all_users=bool(data['is_all_users']))['receiver'])

        if request.form['uploadtype'] == 'remove':
            SenderReceiver.remove(pid=team.pid, cid=cid)

            return jsonify({'file': [],
                            'uploadtype': f"{html.escape(request.form['uploadtype'])}",
                            })

        if request.files and 'file' in request.files:
            csv_file = list(csv.DictReader(io.StringIO(
                request.files['file'].read().decode('utf8'))))
            if request.form['uploadtype'] == 'replace':
                SenderReceiver.replace(
                    pid=team.pid, cid=cid, datas=csv_file)
            elif request.form['uploadtype'] == 'update':
                SenderReceiver.update(pid=team.pid, cid=cid, datas=csv_file)

            return jsonify({'file': csv_file,
                            'uploadtype': f"{html.escape(request.form['uploadtype'])}",
                            })

    return make_response({}, 404)


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/schedule', methods=('GET', 'POST'))
def campaign_schedule(pid: str, tid: str, cid: str) -> str | ResponseBase:
    ''' campaign schedule '''
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-return-statements
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

    campaign_data = SenderCampaign.get(
        cid=cid, pid=team.pid, tid=team.id)
    if request.method == 'GET':
        return render_template('./sender_campaign_schedule.html',
                               campaign=campaign_data, team=team.dict(by_alias=True))

    if request.method == 'POST':
        data = request.get_json()

        if data and 'casename' in data and data['casename'] == 'getlogs':
            logs = []
            for log in SenderLogs.get(cid=cid):
                logs.append({
                    'time': arrow.get(log['create_at']).to(
                            'Asia/Taipei').format('YYYY-MM-DD HH:mm:ss'),
                    'cid': log['cid'],
                    'count': len(log['receivers']),
                    'layout': log['layout'],
                    'desc': log['desc'],
                })

            return jsonify({'logs': logs})

        if campaign_data and data and 'casename' in data and data['casename'] == 'send':
            user_datas = []

            fields_user, raws_user = SenderReceiver.get_from_user(
                pid=team.pid, tids=campaign_data['receiver']['teams'])
            for raw in raws_user:
                user_datas.append(dict(zip(fields_user, raw)))

            fields, raws = SenderReceiver.get(pid=team.pid, cid=cid)
            for raw in raws:
                user_datas.append(dict(zip(fields, raw)))

            if 'team_w_tags' in campaign_data['receiver'] and \
                    team.id in campaign_data['receiver']['team_w_tags'] and \
                    campaign_data['receiver']['team_w_tags'][team.id]:
                fields_tag, raws_tag = SenderReceiver.get_by_tags(
                    pid=team.pid, tid=team.id,
                    tags=campaign_data['receiver']['team_w_tags'][team.id])

                for raw_tuple in raws_tag:
                    user_datas.append(dict(zip(fields_tag, raw_tuple)))

            if campaign_data['receiver']['all_users']:
                fields_all, raws_all = SenderReceiver.get_all_users()
                for raw_tuple in raws_all:
                    user_datas.append(dict(zip(fields_all, raw_tuple)))

            dist_user_datas = []
            emails = set()
            for user_data in user_datas:
                if user_data['mail'] not in emails:
                    emails.add(user_data['mail'])
                    dist_user_datas.append(user_data)

            SenderLogs.save(cid=cid,
                            layout=campaign_data['mail']['layout'],
                            desc='Send', receivers=dist_user_datas)

            source = None
            if campaign_data['mail']['layout'] == '2':
                if team.mailling:
                    source = {'name': team.name, 'mail': team.mailling}
                    if not (source['name'].startswith('COSCUP') or
                            source['name'].startswith('coscup')):
                        source['name'] = f"COSCUP {source['name']}"
                else:
                    source = {'name': 'COSCUP Attendee',
                              'mail': 'attendee@coscup.org'}

            sender_mailer_start.apply_async(kwargs={
                'campaign_data': campaign_data, 'team_name': team.name, 'source': source,
                'user_datas': dist_user_datas, 'layout': campaign_data['mail']['layout']})

            return jsonify({})

        if campaign_data and data and 'casename' in data and data['casename'] == 'sendtest':
            # layout, campaign_data, team, uids
            user_datas = []

            fields_user, raws_user = SenderReceiver.get_from_user(
                pid=team.pid, tids=campaign_data['receiver']['teams'])
            if raws_user:
                user_datas.append(
                    dict(zip(fields_user, random.choice(raws_user))))

            fields, raws = SenderReceiver.get(pid=team.pid, cid=cid)
            if raws:
                user_datas.append(dict(zip(fields, random.choice(raws))))

            if 'team_w_tags' in campaign_data['receiver'] and \
                    team.id in campaign_data['receiver']['team_w_tags'] and \
                    campaign_data['receiver']['team_w_tags'][team.id]:
                fields_tag, raws_tag = SenderReceiver.get_by_tags(
                    pid=team.pid, tid=team.id,
                    tags=campaign_data['receiver']['team_w_tags'][team.id])
                if raws_tag:
                    user_datas.append(
                        dict(zip(fields_tag, random.choice(raws_tag))))

            if campaign_data['receiver']['all_users']:
                fields_all, raws_all = SenderReceiver.get_all_users()
                if raws_all:
                    user_datas.append(
                        dict(zip(fields_all, random.choice(raws_all))))

            uid = g.user['account']['_id']
            users = User.get_info(uids=[uid, ])

            dist_user_datas = [random.choice(user_datas), ]

            for user_data in dist_user_datas:
                user_data.update({
                    'mail': users[uid]['oauth']['email'],
                })

            SenderLogs.save(cid=cid,
                            layout=campaign_data['mail']['layout'],
                            desc='Test Send', receivers=dist_user_datas)

            source = None
            if campaign_data['mail']['layout'] == '2':
                if team.mailling:
                    source = {'name': team.name, 'mail': team.mailling}
                    if not (source['name'].startswith('COSCUP') or
                            source['name'].startswith('coscup')):
                        source['name'] = f"COSCUP {source['name']}"
                else:
                    source = {'name': 'COSCUP Attendee',
                              'mail': 'attendee@coscup.org'}

            sender_mailer_start.apply_async(kwargs={
                'campaign_data': campaign_data, 'team_name': team.name, 'source': source,
                'user_datas': dist_user_datas, 'layout': campaign_data['mail']['layout']})

            return jsonify({})

    return make_response({}, 404)
