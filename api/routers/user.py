''' User '''
from typing import Any

import arrow
import phonenumbers
from fastapi import APIRouter, Depends, status

from api.apistructs.items import ProjectItem, TeamItem
from api.apistructs.users import (UserMeAddressInput, UserMeAddressOutput,
                                  UserMeBankInput, UserMeBankOut, UserMeOut,
                                  UserMeParticipatedItem,
                                  UserMeParticipatedOut, UserMeProfileInput,
                                  UserMeProfileOutput, UserMeProfileRealInput,
                                  UserMeProfileRealOutput)
from api.dependencies import get_current_user
from module.project import Project
from module.team import Team
from module.users import User
from structs.users import UserAddress, UserBank, UserProfle, UserProfleRealBase

router = APIRouter(
    prefix='/user',
    tags=['user'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/me',
            summary='Current user info',
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
            summary='Joined team list',
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
            team=TeamItem.parse_obj({'id': team['tid'],
                                     'name': team['name'],
                                     'pid': project['_id']}),
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


@router.get('/me/bank',
            summary="Current user's bank info",
            response_model=UserMeBankOut)
async def me_bank(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeBankOut:
    ''' Get current user's bank info '''
    return UserMeBankOut.parse_obj(
        User.get_bank(uid=current_user['uid']))


@router.put('/me/bank',
            summary="Update current user's bank info",
            response_model=UserMeBankOut)
async def me_bank_update(
        update_data: UserMeBankInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeBankOut:
    ''' Update current user's bank info '''
    data = User.update_bank(
        uid=current_user['uid'], data=UserBank.parse_obj(update_data))
    return UserMeBankOut.parse_obj(data)


@router.get('/me/address',
            summary="Current user's address info",
            response_model=UserMeAddressOutput)
async def me_address(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeAddressOutput:
    ''' Get current user's Address info '''
    return UserMeAddressOutput.parse_obj(
        User.get_address(uid=current_user['uid']))


@router.put('/me/address',
            summary="Update current user's address info",
            response_model=UserMeAddressOutput)
async def me_address_update(
        update_data: UserMeAddressInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeAddressOutput:
    ''' Update current user's address info '''
    data = User.update_address(
        uid=current_user['uid'], data=UserAddress.parse_obj(update_data))
    return UserMeAddressOutput.parse_obj(data)


@router.get('/me/profile',
            summary="Get current's profile",
            response_model=UserMeProfileOutput)
async def me_profile(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeProfileOutput:
    ''' Get current user's profile and the `intro` in Markdown format '''
    data = User(uid=current_user['uid']).get_profile()
    if data:
        return UserMeProfileOutput.parse_obj(data)

    return UserMeProfileOutput.parse_obj({})


@router.put('/me/profile',
            summary="Update current's profile",
            response_model=UserMeProfileOutput)
async def me_profile_update(
        update_data: UserMeProfileInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeProfileOutput:
    ''' Update current user's profile and the `intro` in Markdown format '''
    data = User(uid=current_user['uid']).update_profile(
        UserProfle.parse_obj(update_data).dict()
    )
    return UserMeProfileOutput.parse_obj(data['profile'])


@router.get('/me/profile_real',
            summary="Get current's real profile",
            response_model=UserMeProfileRealOutput)
async def me_profile_real(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeProfileRealOutput:
    ''' Get current user's real profile '''
    return UserMeProfileRealOutput.parse_obj(
        User(uid=current_user['uid']).get_profile_real())


@router.put('/me/profile_real',
            summary="Update current's real profile",
            response_model=UserMeProfileRealOutput)
async def me_profile_real_update(
        update_data: UserMeProfileRealInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeProfileRealOutput:
    ''' Update current user's real profile '''
    need_update = UserProfleRealBase.parse_obj(update_data)
    phone: str = ''

    try:
        phone = phonenumbers.format_number(
            phonenumbers.parse(need_update.phone),
            phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.phonenumberutil.NumberParseException:
        ...

    need_update.phone = phone
    data = User(uid=current_user['uid']).get_profile_real()
    saved = User(uid=current_user['uid']).update_profile_real_base(
        data=data.copy(update=need_update.dict()))

    return UserMeProfileRealOutput.parse_obj(saved)
