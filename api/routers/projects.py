''' Projects '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.apistructs.items import ProjectItem, TeamItem
from api.apistructs.projects import (ProjectAllOut, ProjectCreateInput,
                                     ProjectCreateOutput,
                                     ProjectItemUpdateInput,
                                     ProjectItemUpdateOutput,
                                     ProjectSettingTrafficSubsidyInput,
                                     ProjectSettingTrafficSubsidyOutput,
                                     ProjectTeamDietaryHabitOutput,
                                     ProjectTeamsOutput)
from api.apistructs.teams import TeamCreateInput, TeamCreateOutput
from api.dependencies import get_current_user
from module.dietary_habit import DietaryHabitItemsName, DietaryHabitItemsValue
from module.form import FormTrafficFeeMapping
from module.project import Project
from module.team import Team
from module.users import User
from setting import API_DEFAULT_OWNERS
from structs.projects import ProjectBaseUpdate

router = APIRouter(
    prefix='/projects',
    tags=['projects'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('',
            summary='List all projects.',
            response_model=ProjectAllOut,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def projects_all(current_user: dict[str, Any] = Depends(get_current_user)) -> ProjectAllOut:
    ''' List all projects '''
    datas = []
    for data in Project.all():
        if current_user['uid'] in data.owners:
            datas.append(ProjectItem.parse_obj(data))
        else:
            datas.append(
                ProjectItem.parse_obj({
                    'id': data.id,
                    'name': data.name,
                    'desc': data.desc,
                }))

    return ProjectAllOut(datas=datas)


@router.post('',
             summary='Create a project.',
             response_model=ProjectCreateOutput,
             responses={
                 status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
             response_model_by_alias=False,
             response_model_exclude_none=True,
             )
async def projects_create(
        create_date: ProjectCreateInput,
        current_user: dict[str, Any] = Depends(get_current_user)) -> ProjectCreateOutput:
    ''' List all projects '''
    if current_user['uid'] not in API_DEFAULT_OWNERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    data = create_date.dict()
    data['owners'] = API_DEFAULT_OWNERS
    result = Project.create(**data)
    return ProjectCreateOutput.parse_obj(result)


@router.patch('/{pid}',
              summary='Update one project info. *owners',
              tags=['owners', ],
              response_model=ProjectItemUpdateOutput,
              responses={
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                  status.HTTP_401_UNAUTHORIZED: {'description': '`owners` permission required'},
              },
              response_model_exclude_none=True,
              )
async def projects_one_update(
        update_data: ProjectItemUpdateInput,
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(get_current_user),
) -> ProjectItemUpdateOutput | None:
    ''' Update one project info

    Permissions
    -----------
    - **owners**

    '''

    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user['uid'] not in project.owners:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    result = Project.update(pid=pid,
                            data=ProjectBaseUpdate.parse_obj(update_data))

    return ProjectItemUpdateOutput.parse_obj(result)


@router.get('/{pid}/teams',
            summary='Lists of teams in project.',
            response_model=ProjectTeamsOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def projects_teams(
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user),
) -> ProjectTeamsOutput | None:
    ''' Lists of teams in project '''
    teams = []
    for team in Team.list_by_pid(pid=pid):
        teams.append(TeamItem.parse_obj(team))

    return ProjectTeamsOutput.parse_obj({'teams': teams})


@router.post('/{pid}/teams',
             summary='Create a new team in project.',
             response_model=TeamCreateOutput,
             responses={
                 status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
             response_model_by_alias=False,
             response_model_exclude_none=True,
             )
async def projects_teams_create(
        create_date: TeamCreateInput,
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user),
) -> TeamCreateOutput | None:
    ''' Create a new team in project '''
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user['uid'] not in project.owners:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    result = Team.create(
        pid=pid, tid=create_date.id, name=create_date.name, owners=project.owners)

    return TeamCreateOutput.parse_obj(result)


@router.get('/{pid}/teams/dietary_habit',
            summary='Lists of dietary habit statistics in project.',
            response_model=list[ProjectTeamDietaryHabitOutput],
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def projects_teams_dietary_habit(
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user),
) -> list[ProjectTeamDietaryHabitOutput] | None:
    ''' Lists of dietary habit statistics in project '''
    all_users = {}
    for team in Team.list_by_pid(pid=pid):
        if team.chiefs:
            for uid in team.chiefs:
                all_users[uid] = {'tid': team.id}

        if team.members:
            for uid in team.members:
                all_users[uid] = {'tid': team.id}

    user_infos = User.get_info(
        uids=list(all_users.keys()), need_sensitive=True)

    habit_count = {}
    for data in User.marshal_dietary_habit(user_infos=user_infos):
        for habit in data['dietary_habit']:
            if habit not in habit_count:
                habit_count[habit] = 0

            habit_count[habit] += 1

    dietary_habit_info = {}
    for item in DietaryHabitItemsValue:
        dietary_habit_info[item.value] = DietaryHabitItemsName[item.name].value

    datas = []
    for habit, count in habit_count.items():
        datas.append(
            ProjectTeamDietaryHabitOutput.parse_obj({'name': dietary_habit_info[habit],
                                                     'count': count,
                                                     'code': habit,
                                                     }))

    return datas


@router.get('/{pid}/setting/traffic_subsidy',
            summary='Get traffic subsidy lists. *owners',
            tags=['owners', ],
            response_model=ProjectSettingTrafficSubsidyOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                status.HTTP_401_UNAUTHORIZED: {'description': '`owners` permission required'},
            },
            )
async def projects_traffic(
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(get_current_user),
) -> ProjectSettingTrafficSubsidyOutput:
    ''' Get traffic subsidy lists

    Permissions
    -----------
    - **owners**

    '''

    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user['uid'] not in project.owners:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return ProjectSettingTrafficSubsidyOutput.parse_obj({
        'datas': FormTrafficFeeMapping.get(pid=pid)})


@router.put('/{pid}/setting/traffic_subsidy',
            summary='Update traffic subsidy lists (replace) *owners',
            tags=['owners', ],
            response_model=ProjectSettingTrafficSubsidyOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'},
                status.HTTP_401_UNAUTHORIZED: {'description': '`owners` permission required'},
            },
            )
async def projects_traffic_update(
        update_data: ProjectSettingTrafficSubsidyInput,
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(get_current_user),
) -> ProjectSettingTrafficSubsidyOutput:
    ''' Update traffic subsidy lists (replace)

    Permissions
    -----------
    - **owners**

    '''

    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user['uid'] not in project.owners:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    result = FormTrafficFeeMapping.save(pid=pid, datas=update_data.datas)

    return ProjectSettingTrafficSubsidyOutput.parse_obj({'datas': result})
