''' Main '''
import hashlib
from typing import Any, Optional

from fastapi import FastAPI, Query, status
from fastapi.responses import JSONResponse, RedirectResponse

from api.apistructs.members import (  # pylint: disable=import-error
    MembersInfo, MembersOut, MembersTeams)
from api.routers import members  # pylint: disable=import-error
from module.team import Team  # pylint: disable=import-error
from module.users import User  # pylint: disable=import-error

app = FastAPI(
    title='Volunteer API.',
    description='API services.',
    version='2022.09.30',
    root_path="/api",
    contact={'name': 'Volunteer Team',
             'url': 'https://volunteer.coscup.org/',
             'email': 'volunteer@coscup.org',
             },
    license_info={'name': 'AGPL-3.0',
                  'url': 'https://github.com/COSCUP/COSCUP-Volunteer/blob/master/LICENSE.txt',
                  },
)

app.include_router(members.router)


@app.get('/', tags=['docs', ],
         summary='API main page.',
         response_class=RedirectResponse, status_code=302)
async def index() -> Optional[str]:
    '''Main page '''
    return f'{app.root_path}{app.docs_url}'


@app.get('/members', tags=['members', ],
         summary='Get members (deprecated).',
         responses={status.HTTP_404_NOT_FOUND: {
             'description': 'Project not found'}},
         response_model=MembersOut,
         deprecated=True,
         )
async def members_past(
        pid: str = Query(description='Project ID.', example='2022')) -> dict[str, Any]:
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
