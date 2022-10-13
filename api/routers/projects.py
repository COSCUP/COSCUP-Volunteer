''' Projects '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.apistructs.items import ProjectItem, TeamItem
from api.apistructs.projects import (ProjectAllOut, ProjectItemUpdateInput,
                                     ProjectItemUpdateOutput,
                                     ProjectTeamDietaryHabitOutput,
                                     ProjectTeamsOutput)
from api.dependencies import get_current_user
from module.dietary_habit import DietaryHabitItemsName, DietaryHabitItemsValue
from module.project import Project
from module.team import Team
from module.users import User
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
                    'id': data['_id'],
                    'name': data['name'],
                    'desc': data['desc'],
                }))

    return ProjectAllOut(datas=datas)


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
        for uid in team['chiefs']+team['members']:
            all_users[uid] = {'tid': team['tid']}

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
