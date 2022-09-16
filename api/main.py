''' Main '''
import hashlib
from typing import Any, Optional

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from module.team import Team
from module.users import User

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


@app.get('/', response_class=RedirectResponse, status_code=302)
async def root() -> Optional[str]:
    ''' Root page '''
    return f'{app.root_path}{app.docs_url}'


class MembersInfo(BaseModel):
    ''' MembersInfo '''
    name: str = Field(description='User name or display name')
    email_hash: str = Field(description='Email hashed in MD5')


class MembersTeams(BaseModel):
    ''' MembersTeams '''
    name: str = Field(description='Team name')
    tid: str = Field(description='Team id')
    chiefs: list[MembersInfo] = Field(default=[], description='All chiefs')
    members: list[MembersInfo] = Field(default=[], description='All members')


class MembersOut(BaseModel):
    ''' MembersOut '''
    data: list[MembersTeams] = Field(default=[], description='All teams info.')


@app.get('/members', tags=['members', ],
         responses={status.HTTP_404_NOT_FOUND: {
             'description': 'Project not found'}},
         response_model=MembersOut)
async def members(pid: str) -> dict[str, Any]:
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
