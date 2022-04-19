''' API '''
import hashlib

from flask import Blueprint, jsonify, request

from module.team import Team
from module.users import User

VIEW_API = Blueprint('api', __name__, url_prefix='/api')


@VIEW_API.route('/')
def index():
    ''' Index page '''
    return 'hi'


@VIEW_API.route('/members')
def project_members():
    ''' List all members '''
    pid = request.args['pid']

    result = []
    for team in Team.list_by_pid(pid=pid):
        data = {}
        data['name'] = team['name']
        data['tid'] = team['tid']

        data['chiefs'] = []
        for user in User.get_info(uids=team['chiefs']).values():
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data['chiefs'].append({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            })

        data['members'] = []
        for user in User.get_info(uids=list(set(team['members']) - set(team['chiefs']))).values():
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data['members'].append({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            })

        result.append(data)

    return jsonify({'data': result})
