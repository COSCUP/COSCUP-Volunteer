import json
import logging

from flask import Blueprint
from flask import g
from flask import jsonify
from flask import render_template
from flask import request
from markdown import markdown

from celery_task.task_sendermailer import sender_mailer_volunteer
from module.sender import SenderCampaign
from module.team import Team
from module.users import User
from view.utils import check_the_team_and_project_are_existed

VIEW_SENDER = Blueprint('sender', __name__, url_prefix='/sender')


@VIEW_SENDER.route('/<pid>/<tid>/', methods=('GET', 'POST'))
def index(pid, tid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    ''' ..note::
        1. create campaign (campaign name) / list campaign
        2. write title, content(jinja2, markdown)
        3. pick up receiver
        4. send / send test

    '''

    if request.method == 'GET':
        return render_template('./sender.html')

    elif request.method == 'POST':
        data = request.get_json()

        if 'casename' in data and data['casename'] == 'get':
            return jsonify({'campaigns': list(SenderCampaign.get_list(pid=team['pid'], tid=team['tid']))})

        if 'casename' in data and data['casename'] == 'create':
            r = SenderCampaign.create(
                    name=data['name'], pid=team['pid'], tid=team['tid'], uid=g.user['account']['_id'])

            return jsonify({'cid': r['_id']})


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/', methods=('GET', 'POST'))
def campaign(pid, tid, cid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    campaign_data = SenderCampaign.get(cid=cid, pid=pid, tid=tid)

    return render_template('./sender_campaign_index.html', campaign=campaign_data, team=team)


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/content', methods=('GET', 'POST'))
def campaign_content(pid, tid, cid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    if request.method == 'GET':
        campaign_data = SenderCampaign.get(cid=cid, pid=team['pid'], tid=team['tid'])

        return render_template('./sender_campaign_content.html', campaign=campaign_data, team=team)

    elif request.method == 'POST':
        data = request.get_json()

        if 'casename' in data and data['casename'] == 'get':
            campaign_data = SenderCampaign.get(cid=cid, pid=team['pid'], tid=team['tid'])
            return jsonify({'mail': campaign_data['mail']})

        if 'casename' in data and data['casename'] == 'save':
            r = SenderCampaign.save_mail(
                cid=cid,
                subject=data['data']['subject'].strip(),
                content=data['data']['content'].strip(),
                preheader=data['data']['preheader'].strip(),
                layout=data['data']['layout'].strip(),
            )
            return jsonify({'mail': r['mail']})


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/receiver', methods=('GET', 'POST'))
def campaign_receiver(pid, tid, cid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    campaign_data = SenderCampaign.get(cid=cid, pid=team['pid'], tid=team['tid'])
    if request.method == 'GET':
        return render_template('./sender_campaign_receiver.html', campaign=campaign_data, team=team)

    if request.method == 'POST':
        data = request.get_json()

        if 'casename' in data and data['casename'] == 'getinit':
            teams = []
            for team in Team.list_by_pid(pid=team['pid']):
                teams.append({'tid': team['tid'], 'name': team['name']})

            return jsonify({'teams': teams, 'pickteams': campaign_data['receiver']['teams']})

        if 'casename' in data and data['casename'] == 'save':
            tids = [team['tid'] for team in Team.list_by_pid(pid=team['pid'])]

            _result = []
            for tid in tids:
                if tid in data['pickteams']:
                    _result.append(tid)

            return jsonify(SenderCampaign.save_receiver(cid=cid, teams=_result)['receiver'])


@VIEW_SENDER.route('/<pid>/<tid>/campaign/<cid>/schedule', methods=('GET', 'POST'))
def campaign_schedule(pid, tid, cid):
    team, project, _redirect = check_the_team_and_project_are_existed(pid=pid, tid=tid)
    if _redirect:
        return _redirect

    campaign_data = SenderCampaign.get(cid=cid, pid=team['pid'], tid=team['tid'])
    if request.method == 'GET':
        return render_template('./sender_campaign_schedule.html', campaign=campaign_data, team=team)

    if request.method == 'POST':
        data = request.get_json()

        if 'casename' in data and data['casename'] == 'send':
            return jsonify(data)

        if 'casename' in data and data['casename'] == 'sendtest':
            # layout, campaign_data, team, uids
            if campaign_data['mail']['layout'] == '1':
                uid = g.user['account']['_id']
                users = User.get_info(uids=[uid, ])

                user_data = {
                    'mail': users[uid]['oauth']['email'],
                    'name': users[uid]['profile']['badge_name'],
                }

                sender_mailer_volunteer.apply_async(kwargs={
                        'campaign_data': campaign_data, 'team_name': team['name'],
                        'user_datas': (user_data, )})

            return jsonify(data)
