''' Members '''
import hashlib

from fastapi import APIRouter, Path, Query, status
from fastapi.responses import JSONResponse

from api.apistructs.members import MembersInfo, MembersOut, MembersTeams
from module.team import Team
from module.users import User

router = APIRouter(
    prefix='/members',
    tags=['members'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('', tags=['members', ],
            summary='Get members (deprecated).',
            responses={status.HTTP_404_NOT_FOUND: {
                'description': 'Project not found'}},
            response_model=MembersOut,
            deprecated=True,
            )
async def members_past(
        pid: str = Query(description='Project ID.', example='2022')) -> MembersOut | JSONResponse:
    ''' Get Project's members

        **Warning: will be deprecated.**

    '''
    result = MembersOut()
    for team in Team.list_by_pid(pid=pid):
        data = {}
        data['name'] = team['name']
        data['tid'] = team['tid']

        data['chiefs'] = []
        chiefs_infos = User.get_info(uids=team['chiefs'])
        for uid in team['chiefs']:
            if uid not in chiefs_infos:
                continue

            _user = chiefs_infos[uid]
            h_msg = hashlib.md5()
            h_msg.update(_user['oauth']['email'].encode('utf-8'))
            data['chiefs'].append(MembersInfo.parse_obj({
                'name': _user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        data['members'] = []
        for _user in User.get_info(uids=list(set(team['members']) - set(team['chiefs']))).values():
            h_msg = hashlib.md5()
            h_msg.update(_user['oauth']['email'].encode('utf-8'))
            data['members'].append(MembersInfo.parse_obj({
                'name': _user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        result.data.append(MembersTeams.parse_obj(data))

    if result.data:
        return result

    return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)


@router.get('/{pid:str}',
            responses={status.HTTP_404_NOT_FOUND: {
                'description': 'Project not found'}},
            response_model=MembersOut)
async def members(
        pid: str = Path(description='Project ID.', example='2022')) -> MembersOut | JSONResponse:
    ''' Get Project's members '''
    result = MembersOut()
    for team in Team.list_by_pid(pid=pid):
        data = {}
        data['name'] = team['name']
        data['tid'] = team['tid']

        data['chiefs'] = []
        chiefs_infos = User.get_info(uids=team['chiefs'])
        for uid in team['chiefs']:
            if uid not in chiefs_infos:
                continue

            user = chiefs_infos[uid]
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data['chiefs'].append(MembersInfo.parse_obj({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        data['members'] = []
        for user in User.get_info(uids=list(set(team['members']) - set(team['chiefs']))).values():
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data['members'].append(MembersInfo.parse_obj({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        result.data.append(MembersTeams.parse_obj(data))

    if result.data:
        return result

    return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)
