''' Teams '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.apistructs.items import TeamItem, UserItem
from api.apistructs.teams import (TeamAddressBookOutput, TeamItemUpdateInput,
                                  TeamItemUpdateOutput)
from api.dependencies import get_current_user
from module.mattermost_bot import MattermostTools
from module.team import Team
from module.users import User

router = APIRouter(
    prefix='/teams',
    tags=['teams'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/{pid}/{tid}',
            summary='Get team info',
            response_model=TeamItem,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def teams_one(
        pid: str,
        tid: str,
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TeamItem | None:
    ''' Get one team info

    - **pid**: project id
    - **tid**: team id

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return TeamItem.parse_obj(team)


@router.patch('/{pid}/{tid}',
              summary='Update team info',
              response_model=TeamItemUpdateOutput,
              responses={
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
              response_model_exclude_none=True,
              )
async def teams_one_update(
        pid: str,
        tid: str,
        update_data: TeamItemUpdateInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> TeamItemUpdateOutput:
    ''' Update one team info

    - **pid**: project id
    - **tid**: team id
    - **update_data**: The data need to update.

    Permissions
    -----------
    - **owners**: can update all fields.
    - **chiefs**: can update the fields of ``name``, `desc`.

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    include: set[str] | None
    if current_user['uid'] in team['owners']:
        include = None

    elif current_user['uid'] in team['chiefs']:
        include = {'name', 'desc'}

    if current_user['uid'] in team['owners'] or include is not None:
        updated = Team.update_setting(
            pid=pid, tid=tid, data=update_data.dict(include=include))

    return TeamItemUpdateOutput.parse_obj(updated)


@router.get('/{pid}/{tid}/addressbook',
            summary='Get the address book info of team members.',
            response_model=TeamAddressBookOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def teams_one_address_book(
        pid: str,
        tid: str,
        current_user: dict[str, Any] = Depends(get_current_user)) -> TeamAddressBookOutput:
    ''' Get the address book of team members

    - **pid**: project id
    - **tid**: team id

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user['uid'] not in (team['owners'] + team['chiefs'] + team['members']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    uids = set()
    uids.update(team['chiefs'])
    uids.update(team['members'])
    users_info = User.get_info(uids=list(uids))

    datas = []
    for uid in uids:
        chat: dict[str, str] | None = None
        mid = MattermostTools.find_possible_mid(uid=uid)
        if mid:
            chat = {'mid': mid,
                    'name': MattermostTools.find_user_name(mid=mid)}

        datas.append(UserItem.parse_obj(
            {'id': uid,
             'badge_name': users_info[uid]['profile']['badge_name'],
             'avatar': users_info[uid]['oauth']['picture'],
             'is_chief': uid in team['chiefs'],
             'chat': chat,
             }))

        datas.sort(key=lambda data: data.is_chief or False, reverse=True)

    return TeamAddressBookOutput.parse_obj({'datas': datas})
