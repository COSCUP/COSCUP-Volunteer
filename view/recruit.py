''' recruit.py '''
from flask import (Blueprint, g, jsonify, redirect, render_template,
                   request)
from werkzeug.wrappers import Response as ResponseBase

from module.skill import (RecruitQuery, SkillEnum, SkillEnumDesc, StatusEnum,
                          StatusEnumDesc, TeamsEnum, TeamsEnumDesc)
from module.users import TobeVolunteer, User
from structs.teams import TeamUsers
from view.utils import check_the_team_and_project_are_existed

VIEW_RECRUIT = Blueprint('recruit', __name__, url_prefix='/recruit')


@VIEW_RECRUIT.route('/<pid>/<tid>/list', methods=('GET', 'POST'))
def recurit_list(pid: str, tid: str) -> str | ResponseBase:  # pylint: disable=too-many-return-statements
    ''' List page '''
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
        return render_template('./recruit_list.html',
                               project=project.dict(by_alias=True),
                               team=team.dict(by_alias=True), is_admin=is_admin)

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            return jsonify({
                'team_enum': {key: item.value for key, item in TeamsEnum.__members__.items()},
                'team_enum_desc': {key: item.value for key, item in
                                   TeamsEnumDesc.__members__.items()},
                'skill_enum': {key: item.value for key, item in
                               SkillEnum.__members__.items()},
                'skill_enum_desc': {key: item.value for key, item in
                                    SkillEnumDesc.__members__.items()},
                'status_enum': {key: item.value for key, item in StatusEnum.__members__.items()},
                'status_enum_desc': {key: item.value for key, item in
                                     StatusEnumDesc.__members__.items()},
            })

        if post_data and post_data['casename'] == 'query':
            query = RecruitQuery.parse_obj(post_data['query']).dict()
            data = list(TobeVolunteer.query(query))

            users_info = User.get_info(uids=[user['uid'] for user in data])

            suspend_uids: dict[str, None] = {}
            for raw_user in User.get_suspend_uids(uids=[user['uid'] for user in data]):
                suspend_uids[raw_user['_id']] = None

            result = []
            for member in data:
                if member['uid'] in suspend_uids:
                    continue

                member.update({
                    'profile': {'badge_name': users_info[member['uid']]['profile']['badge_name']},
                    'oauth': {'picture': users_info[member['uid']]['oauth']['picture']}})

                result.append(member)

            return jsonify({'members': result})

    return jsonify({})
