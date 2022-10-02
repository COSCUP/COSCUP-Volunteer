''' Projects '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from api.apistructs.projects import ProjectAllOut
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


@router.get('/{pid}',
            response_model=ProjectItem,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def projects_one(
        pid: str,
        current_user: dict[str, Any] = Depends(get_current_user),
) -> ProjectItem | dict[str, Any] | None:
    ''' Get one project '''
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=404)

    project['id'] = project['_id']
    result = ProjectItem.parse_obj(project)

    if 'owners' in project and current_user['uid'] in project['owners']:
        return result

    return result.dict(include={'id', 'name', 'desc'})
