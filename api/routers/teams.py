''' Teams '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from api.apistructs.items import TeamItem, UserItem
from api.apistructs.teams import (TeamAddressBookOutput,
                                  TeamGetVolunteersOutput, TeamItemUpdateInput,
                                  TeamItemUpdateOutput, TeamUpdateMembers,
                                  TeamUpdateMembersOutput)
from api.dependencies import get_current_user
from module.mattermost_bot import MattermostTools
from module.team import Team
from module.users import User
from structs.teams import TeamUsers

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
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
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
        update_data: TeamItemUpdateInput,
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
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

    teamusers = TeamUsers.parse_obj(team)
    include: set[str] | None = None
    if current_user['uid'] in teamusers.owners:
        include = None

    elif current_user['uid'] in teamusers.chiefs:
        include = {'name', 'desc'}

    updated: dict[str, Any] | None = None
    if current_user['uid'] in teamusers.owners or include is not None:
        updated = Team.update_setting(
            pid=pid, tid=tid, data=update_data.dict(include=include))

    return TeamItemUpdateOutput.parse_obj(updated)


@router.get('/{pid}/{tid}/addressbook',
            summary='Get the address book info of team members.',
            response_model=TeamAddressBookOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                status.HTTP_401_UNAUTHORIZED: {'description': 'You are not the member.'},
            },
            response_model_exclude_none=True,
            )
async def teams_one_address_book(
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> TeamAddressBookOutput:
    ''' Get the address book of team members

    - **pid**: project id
    - **tid**: team id

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs + teamusers.members):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    uids = set()
    uids.update(teamusers.chiefs)
    uids.update(teamusers.members)
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
             'is_chief': uid in teamusers.chiefs,
             'chat': chat,
             }))

        datas.sort(key=lambda data: data.is_chief or False, reverse=True)

    return TeamAddressBookOutput.parse_obj({'datas': datas})


@router.patch('/{pid}/{tid}/chiefs',
              summary='Add users into team as chiefs *owners, *members',
              response_model=TeamUpdateMembersOutput,
              responses={
                  status.HTTP_401_UNAUTHORIZED: {'description': 'You are not the member.'},
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                  status.HTTP_409_CONFLICT: {'description': 'Update fail.'},
              },
              response_model_exclude_none=True,
              )
@router.delete('/{pid}/{tid}/chiefs',
               summary='Remove users from team as chiefs *owners, *members',
               response_model=TeamUpdateMembersOutput,
               responses={
                   status.HTTP_401_UNAUTHORIZED: {'description': 'You are not the member.'},
                   status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                   status.HTTP_409_CONFLICT: {'description': 'Update fail.'},
               },
               response_model_exclude_none=True,
               )
async def teams_chiefs_update(
        update_data: TeamUpdateMembers,
        request: Request,
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> TeamUpdateMembersOutput:
    ''' Update team's chiefs

    - **pid**: project id
    - **tid**: team id

    Permissions
    -----------
    - **owners**
    - **chiefs**

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PATCH':
        Team.update_chiefs(pid=pid, tid=tid, add_uids=update_data.uids)
        return TeamUpdateMembersOutput(status=True)

    if request.method == 'DELETE':
        Team.update_chiefs(pid=pid, tid=tid, del_uids=update_data.uids)
        return TeamUpdateMembersOutput(status=True)

    raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.patch('/{pid}/{tid}/members',
              summary='Add users into team as members *owners, *chiefs',
              response_model=TeamUpdateMembersOutput,
              responses={
                  status.HTTP_401_UNAUTHORIZED: {'description': 'You are not the member.'},
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                  status.HTTP_409_CONFLICT: {'description': 'Update fail.'},
              },
              response_model_exclude_none=True,
              )
@router.delete('/{pid}/{tid}/members',
               summary='Remove users from team as members *owners, *chiefs',
               response_model=TeamUpdateMembersOutput,
               responses={
                   status.HTTP_401_UNAUTHORIZED: {'description': 'You are not the member.'},
                   status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                   status.HTTP_409_CONFLICT: {'description': 'Update fail.'},
               },
               response_model_exclude_none=True,
               )
async def teams_members_update(
        update_data: TeamUpdateMembers,
        request: Request,
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> TeamUpdateMembersOutput:
    ''' Update team's members

    - **pid**: project id
    - **tid**: team id

    Permissions
    -----------
    - **owners**
    - **chiefs**

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if request.method == 'PATCH':
        Team.update_members(pid=pid, tid=tid, add_uids=update_data.uids)
        return TeamUpdateMembersOutput(status=True)

    if request.method == 'DELETE':
        Team.update_members(pid=pid, tid=tid, del_uids=update_data.uids)
        return TeamUpdateMembersOutput(status=True)

    raise HTTPException(status_code=status.HTTP_409_CONFLICT)


@router.get('/{pid}/{tid}/volunteers',
            summary='Get users from team *owners, *chiefs, *members',
            response_model=TeamGetVolunteersOutput,
            responses={
                status.HTTP_401_UNAUTHORIZED: {'description': 'You are not the member.'},
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                status.HTTP_409_CONFLICT: {'description': 'Update fail.'},
            },
            response_model_exclude_none=True,
            )
async def teams_get_volunteers(
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> TeamGetVolunteersOutput:
    ''' Get team's users

    - **pid**: project id
    - **tid**: team id

    Permissions
    -----------
    - **owners**
    - **chiefs**
    - **members**

    '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs+teamusers.members):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user_infos = User.get_info(uids=teamusers.chiefs+teamusers.members)

    result: list[UserItem] = []
    for uid in (set(teamusers.chiefs)-set(teamusers.members)):
        result.append(UserItem(
            id=uid,
            badge_name=user_infos[uid]['profile']['badge_name'],
            avatar=user_infos[uid]['oauth']['picture'],
            is_chief=True,
            intro=None,
            chat=None,
        ))

    for uid in (set(teamusers.members)-set(teamusers.chiefs)):
        result.append(UserItem(
            id=uid,
            badge_name=user_infos[uid]['profile']['badge_name'],
            avatar=user_infos[uid]['oauth']['picture'],
            is_chief=False,
            intro=None,
            chat=None,
        ))

    return TeamGetVolunteersOutput.parse_obj({'datas': result})
