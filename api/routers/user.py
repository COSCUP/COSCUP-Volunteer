''' User '''
from typing import Any

import arrow
from fastapi import APIRouter, Depends, status

from api.apistructs.projects import ProjectItem
from api.apistructs.teams import TeamItem
from api.apistructs.users import (UserMeBankOut, UserMeOut,
                                  UserMeParticipatedItem,
                                  UserMeParticipatedOut)
from api.dependencies import get_current_user
from module.project import Project
from module.team import Team
from module.users import User

router = APIRouter(
    prefix='/user',
    tags=['user'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/me',
            response_model=UserMeOut,
            responses={status.HTTP_404_NOT_FOUND: {
                'description': 'Project not found'}})
async def me_info(current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeOut:
    ''' Get myself user info '''
    user_info = User.get_info(uids=[current_user['uid'], ])[
        current_user['uid']]

    return UserMeOut(
        uid=current_user['uid'],
        badge_name=user_info['profile']['badge_name'],
        avatar=user_info['oauth']['picture'],
        intro=user_info['profile']['intro'],
    )


@router.get('/me/participated',
            response_model=UserMeParticipatedOut,
            response_model_exclude_none=True,
            )
async def me_participated(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeParticipatedOut:
    ''' Get myself participated in lists '''
    participate_in = UserMeParticipatedOut()
    for team in Team.participate_in(current_user['uid']):
        project = Project.get(team['pid'])
        if project is None:
            continue

        data = UserMeParticipatedItem(
            project=ProjectItem.parse_obj(
                {'id': project['_id'], 'name': project['name']}),
            team=TeamItem(id=team['tid'],
                          name=team['name'], pid=project['_id']),
            action=arrow.get(project['action_date']).date(),
        )

        data.title = '???'
        if current_user['uid'] in team['chiefs']:
            data.title = 'chief'
        elif current_user['uid'] in team['members']:
            data.title = 'member'

        participate_in.datas.append(data)

    participate_in.datas = sorted(
        participate_in.datas, key=lambda data: data.action, reverse=True)

    return participate_in


@router.get('/me/bank', response_model=UserMeBankOut)
async def me_bank(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeBankOut:
    ''' Get myself participated in lists '''
    return UserMeBankOut(bank=User.get_bank(uid=current_user['uid']))
