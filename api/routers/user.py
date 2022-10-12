''' User '''
from typing import Any

import phonenumbers
from fastapi import APIRouter, Depends, status
from pydantic import parse_obj_as

from api.apistructs.items import ProjectItem, TeamItem
from api.apistructs.users import (UserMeAddressInput, UserMeAddressOutput,
                                  UserMeBankInput, UserMeBankOut,
                                  UserMeDietaryHabitInput,
                                  UserMeDietaryHabitItem,
                                  UserMeDietaryHabitOutput, UserMeOut,
                                  UserMeParticipatedItem,
                                  UserMeParticipatedOut, UserMeProfileInput,
                                  UserMeProfileOutput, UserMeProfileRealInput,
                                  UserMeProfileRealOutput,
                                  UserMeToBeVolunteerInput,
                                  UserMeToBeVolunteerOptionIntItem,
                                  UserMeToBeVolunteerOptionsOutput,
                                  UserMeToBeVolunteerOptionStrItem,
                                  UserMeToBeVolunteerOutput)
from api.dependencies import get_current_user
from module.dietary_habit import DietaryHabitItemsName, DietaryHabitItemsValue
from module.project import Project
from module.skill import (SkillEnum, SkillEnumDesc, StatusEnum, StatusEnumDesc,
                          TeamsEnum, TeamsEnumDesc)
from module.team import Team
from module.users import TobeVolunteer, User
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
                {'id': project.id, 'name': project.name}),
            team=TeamItem.parse_obj({'id': team['tid'],
                                     'name': team['name'],
                                     'pid': project.id}),
            action=project.action_date,
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


@router.get('/me/dietary_habit',
            summary="Get current's dietary habit",
            response_model=UserMeDietaryHabitOutput)
async def me_dietary_habit(
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeDietaryHabitOutput:
    ''' Get current user's dietary habit items'''
    saved = User(uid=current_user['uid']).get_dietary_habit()

    datas = []
    for item in DietaryHabitItemsValue:
        datas.append(UserMeDietaryHabitItem.parse_obj(
            {
                'name': DietaryHabitItemsName[item.name].value,
                'value': item.value,
                'checked': item in saved,
            }
        ))

    return UserMeDietaryHabitOutput.parse_obj({'data': datas})


@router.put('/me/dietary_habit',
            summary="Update current's dietary habit",
            response_model=UserMeDietaryHabitOutput)
async def me_dietary_habit_update(
        update_data: UserMeDietaryHabitInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> UserMeDietaryHabitOutput:
    ''' Update current user's dietary habit items'''
    checked = parse_obj_as(
        list[DietaryHabitItemsValue], update_data.checked)
    User(uid=current_user['uid']).update_dietary_habit(values=checked)
    result = await me_dietary_habit(current_user=current_user)
    return result


@router.get('/me/to_be_volunteer/options',
            summary="Get all options of to be volunteer",
            response_model=UserMeToBeVolunteerOptionsOutput)
async def me_to_be_volunteer_options(
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)
) -> UserMeToBeVolunteerOptionsOutput:
    ''' Get all options of to be volunteer '''
    result: dict[str,
                 list[UserMeToBeVolunteerOptionIntItem | UserMeToBeVolunteerOptionStrItem]] = {
        'teams': [], 'skills': [], 'status': []}
    for team in TeamsEnum:
        result['teams'].append(
            UserMeToBeVolunteerOptionIntItem.parse_obj({
                'code': team.name,
                'value': team.value,
                'desc': TeamsEnumDesc[team.name].value,
            })
        )

    for skill in SkillEnum:
        result['skills'].append(
            UserMeToBeVolunteerOptionStrItem.parse_obj({
                'code': skill.name,
                'value': skill.value,
                'desc': SkillEnumDesc[skill.name].value,
            })
        )

    for _status in StatusEnum:
        result['status'].append(
            UserMeToBeVolunteerOptionIntItem.parse_obj({
                'code': _status.name,
                'value': _status.value,
                'desc': StatusEnumDesc[_status.name].value,
            })
        )

    return UserMeToBeVolunteerOptionsOutput.parse_obj(result)


@router.get('/me/to_be_volunteer',
            summary="Get to be volunteer",
            response_model=UserMeToBeVolunteerOutput)
async def me_to_be_volunteer(
        current_user: dict[str, Any] = Depends(get_current_user)
) -> UserMeToBeVolunteerOutput:
    ''' Get to be volunteer '''
    return UserMeToBeVolunteerOutput.parse_obj(
        {'data': TobeVolunteer.get(uid=current_user['uid'])}
    )


@router.put('/me/to_be_volunteer',
            summary="Update to be volunteer",
            response_model=UserMeToBeVolunteerOutput)
async def me_to_be_volunteer_update(
        update_data: UserMeToBeVolunteerInput,
        current_user: dict[str, Any] = Depends(get_current_user)
) -> UserMeToBeVolunteerOutput:
    ''' Update to be volunteer '''
    data = update_data.dict()
    data['uid'] = current_user['uid']
    TobeVolunteer.save(data=data)
    result = await me_to_be_volunteer(current_user=current_user)
    return result
