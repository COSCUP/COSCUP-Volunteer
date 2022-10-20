''' API '''
import hashlib

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field
from werkzeug.wrappers import Response as ResponseBase

from module.team import Team
from module.users import User
from structs.teams import TeamUsers

VIEW_API = Blueprint('api', __name__, url_prefix='/api')


@VIEW_API.route('/')
def index() -> str:
    ''' Index page '''
    return 'hi'


class Member(BaseModel):
    ''' Member '''
    name: str
    email_hash: str


class ProjectMembersOutput(BaseModel):
    ''' ProjectMembersOutput '''
    name: str = Field(default='')
    tid: str = Field(default='')
    chiefs: list[Member] = Field(default_factory=list)
    members: list[Member] = Field(default_factory=list)


@VIEW_API.route('/members')
def project_members() -> ResponseBase:
    ''' List all members '''
    pid = request.args['pid']

    result = []
    for team in Team.list_by_pid(pid=pid):
        data = ProjectMembersOutput()
        data.name = team.name
        data.tid = team.id

        teamusers = TeamUsers.parse_obj(team)
        chiefs_infos = User.get_info(uids=teamusers.chiefs)
        for uid in teamusers.chiefs:
            if uid not in chiefs_infos:
                continue

            user = chiefs_infos[uid]
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data.chiefs.append(Member.parse_obj({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        for user in User.get_info(
                uids=list(set(teamusers.members) - set(teamusers.chiefs))).values():
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data.members.append(Member.parse_obj({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        result.append(data.dict())

    return jsonify({'data': result})
