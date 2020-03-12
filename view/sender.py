import json
import logging

from flask import Blueprint
from flask import g
from flask import jsonify
from flask import render_template
from flask import request

from module.sender import SenderCampaign
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

    return render_template('./sender_campaign.html', campaign=campaign_data, team=team)


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
        logging.info(data)

        if 'casename' in data and data['casename'] == 'get':
            campaign_data = SenderCampaign.get(cid=cid, pid=team['pid'], tid=team['tid'])
            return jsonify({'mail': campaign_data['mail']})

        if 'casename' in data and data['casename'] == 'save':
            r = SenderCampaign.save_mail(
                cid=cid,
                subject=data['data']['subject'].strip(),
                content=data['data']['content'].strip(),
                preheader=data['data']['preheader'].strip(),
            )
            return jsonify({'mail': r['mail']})
