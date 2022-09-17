''' Members '''
import hashlib
from typing import Any

from fastapi import APIRouter, Path, status
from fastapi.responses import JSONResponse

from api.apistructs.members import (  # pylint: disable=import-error
    MembersInfo, MembersOut, MembersTeams)
from module.team import Team  # pylint: disable=import-error
from module.users import User  # pylint: disable=import-error

router = APIRouter(
    prefix='/members',
    tags=['members'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/{pid:str}',
            responses={status.HTTP_404_NOT_FOUND: {
                'description': 'Project not found'}},
            response_model=MembersOut)
async def members(pid: str = Path(description='Project ID.', example='2022')) -> dict[str, Any]:
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
