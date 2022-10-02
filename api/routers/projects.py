''' Projects '''
from typing import Any

import arrow
from fastapi import APIRouter, Depends, HTTPException, status

from api.apistructs.projects import (ProjectAllOut, ProjectItemUpdateInput,
                                     ProjectItemUpdateOutput)
from api.apistructs.users import ProjectItem
from api.dependencies import get_current_user
from module.project import Project

router = APIRouter(
    prefix='/projects',
    tags=['projects'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('',
            response_model=ProjectAllOut,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def projects_all(current_user: dict[str, Any] = Depends(get_current_user)) -> ProjectAllOut:
    ''' List all projects '''
    datas = []
    for data in Project.all():
        if 'owners' in data and current_user['uid'] in data['owners']:
            data['id'] = data['_id']
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
              tags=['owners', ],
              response_model=ProjectItemUpdateOutput,
              responses={
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
              response_model_exclude_none=True,
              )
async def projects_one_update(
        pid: str,
        update_data: ProjectItemUpdateInput,
        current_user: dict[str, Any] = Depends(get_current_user),
) -> ProjectItemUpdateOutput | None:
    ''' Update one project. `Owners only` '''
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if 'owners' not in project or current_user['uid'] not in project['owners']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    data = update_data.dict(exclude_none=True)
    if 'action_date' in data:
        data['action_date'] = arrow.get(data['action_date']).int_timestamp

    Project.update(pid=pid, data=data)

    return ProjectItemUpdateOutput.parse_obj(data)
