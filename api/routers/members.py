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
        pid: str = Query(description='project id', example='2022'),
) -> MembersOut | JSONResponse:
    ''' Get Project's members

        **Warning: will be deprecated.**

    '''
    result = MembersOut()
    for team in Team.list_by_pid(pid=pid):
        if not team.chiefs:
            continue

        data_chiefs: list[MembersInfo] = []
        chiefs_infos = User.get_info(uids=team.chiefs)
        for uid in team.chiefs:
            if uid not in chiefs_infos:
                continue

            _user = chiefs_infos[uid]
            h_msg = hashlib.md5()
            h_msg.update(_user['oauth']['email'].encode('utf-8'))
            data_chiefs.append(MembersInfo.parse_obj({
                'name': _user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        data_members: list[MembersInfo] = []

        uids = set()
        if team.members:
            uids.update(team.members)
        if team.chiefs:
            uids.update(team.chiefs)

        for _user in User.get_info(uids=list(uids)).values():
            h_msg = hashlib.md5()
            h_msg.update(_user['oauth']['email'].encode('utf-8'))
            data_members.append(MembersInfo.parse_obj({
                'name': _user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        result.data.append(MembersTeams.parse_obj(
            {'name': team.name, 'tid': team.id,
             'chiefs': data_chiefs, 'members': data_members}
        ))

    if result.data:
        return result

    return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)


@router.get('/{pid:str}',
            summary='Get members for the staff lists on coscup.org',
            responses={status.HTTP_404_NOT_FOUND: {
                'description': 'Project not found'}},
            response_model=MembersOut)
async def members(
        pid: str = Path(description='project id', example='2022'),
) -> MembersOut | JSONResponse:
    ''' Get Project's members

        For offcial site of coscup.org to fetch and build
        the staff lists page.
    '''
    result = MembersOut()
    for team in Team.list_by_pid(pid=pid):
        if not team.chiefs:
            continue

        data_chiefs: list[MembersInfo] = []
        chiefs_infos = User.get_info(uids=team.chiefs)
        for uid in team.chiefs:
            if uid not in chiefs_infos:
                continue

            user = chiefs_infos[uid]
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data_chiefs.append(MembersInfo.parse_obj({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        data_members: list[MembersInfo] = []

        uids = set()
        if team.members:
            uids.update(team.members)
        if team.chiefs:
            uids.update(team.chiefs)

        for user in User.get_info(uids=list(uids)).values():
            h_msg = hashlib.md5()
            h_msg.update(user['oauth']['email'].encode('utf-8'))
            data_members.append(MembersInfo.parse_obj({
                'name': user['profile']['badge_name'],
                'email_hash': h_msg.hexdigest(),
            }))

        result.data.append(MembersTeams.parse_obj(
            {'name': team.name, 'tid': team.id,
             'chiefs': data_chiefs, 'members': data_members}
        ))

    if result.data:
        return result

    return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)
