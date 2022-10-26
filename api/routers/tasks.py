''' Tasks '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.apistructs.tasks import (TaskCreateInput, TaskCreateOutput,
                                  TaskGetOutput, TasksGetAllOutput,
                                  TaskUpdateInput)
from api.dependencies import get_current_user
from module.project import Project
from module.tasks import Tasks
from module.team import Team
from structs.tasks import TaskItem

router = APIRouter(
    prefix='/tasks',
    tags=['tasks'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/{pid}',
            summary='Get all tasks',
            response_model=TasksGetAllOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_by_alias=False,
            response_model_exclude_none=True,
            )
async def tasks_all(
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TasksGetAllOutput:
    ''' Get all tasks

    - **pid**: project id

    '''
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    is_in_project: bool = False
    for _ in Team.participate_in(uid=current_user['uid'], pid=[pid, ]):
        is_in_project = True
        break

    datas = []
    for task in Tasks.get_by_pid(pid=pid):
        task_data = TaskItem.parse_obj(task)
        if not is_in_project:
            task_data.people = []

        datas.append(task_data)

    return TasksGetAllOutput.parse_obj({'datas': datas})


@router.post('/{pid}',
             summary='Create a task',
             response_model=TaskCreateOutput,
             responses={
                 status.HTTP_401_UNAUTHORIZED: {'description': 'Not members in the project'},
                 status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
             response_model_by_alias=False,
             response_model_exclude_none=True,
             )
async def tasks_create(
        update_data: TaskCreateInput,
        pid: str = Path(..., description='project id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TaskCreateOutput:
    ''' Create a task

    - **pid**: project id

    '''
    is_in_project: bool = False
    for _ in Team.participate_in(uid=current_user['uid'], pid=[pid, ]):
        is_in_project = True
        break

    if not is_in_project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    data = update_data.dict()
    data['pid'] = pid
    data['created_by'] = current_user['uid']
    task_item = TaskItem.parse_obj(data)
    raw = Tasks.add(pid=pid,
                    body=task_item.dict(by_alias=True))

    return TaskCreateOutput.parse_obj(raw)


@router.get('/{pid}/{task_id}',
            summary='Get a task',
            response_model=TaskGetOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
async def tasks_get(
        pid: str = Path(..., description='project id'),
        task_id: str = Path(..., description='task id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TaskGetOutput:
    ''' Get a task

    - **pid**: project id
    - **task_id**: task id

    '''
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task_data = Tasks.get_with_pid(pid=pid, _id=task_id)
    if not task_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    is_in_project: bool = False
    for _ in Team.participate_in(uid=current_user['uid'], pid=[pid, ]):
        is_in_project = True
        break

    if not is_in_project:
        task_data['people'] = []

    return TaskGetOutput.parse_obj(task_data)


@router.patch('/{pid}/{task_id}',
              summary='Update a task (update)',
              response_model=TaskGetOutput,
              responses={
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
              response_model_exclude_none=True,
              )
async def tasks_update(
        update_data: TaskUpdateInput,
        pid: str = Path(..., description='project id'),
        task_id: str = Path(..., description='task id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TaskGetOutput:
    ''' Get a task

    - **pid**: project id
    - **task_id**: task id

    '''
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task_data = Tasks.get_with_pid(pid=pid, _id=task_id)
    if not task_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    is_in_project: bool = False
    for _ in Team.participate_in(uid=current_user['uid'], pid=[pid, ]):
        is_in_project = True
        break

    if not is_in_project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    data = update_data.dict(exclude_none=True)
    data['_id'] = task_id
    data['pid'] = pid

    if data:
        raw = Tasks.add(pid=pid, body=data)
        return TaskGetOutput.parse_obj(raw)

    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
