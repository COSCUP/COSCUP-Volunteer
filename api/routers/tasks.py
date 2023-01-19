''' Tasks '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request, status

from api.apistructs.items import UserItem
from api.apistructs.tasks import (TaskAttendeeInput, TaskCreateInput,
                                  TaskCreateOutput, TaskGetAttendeeOutput,
                                  TaskGetOutput, TaskMeJoinOutput,
                                  TasksGetAllOutput, TaskUpdateInput)
from api.dependencies import get_current_user
from module.project import Project
from module.tasks import Tasks
from module.team import Team
from module.users import User
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


@router.get('/{pid}/{task_id}/attendee',
            summary='Do I join to the task (get)',
            response_model=TaskMeJoinOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            )
@router.post('/{pid}/{task_id}/attendee',
             summary='Join to the task (update)',
             response_model=TaskMeJoinOutput,
             responses={
                 status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
             )
@router.delete('/{pid}/{task_id}/attendee',
               summary='Remove from the task (delete)',
               response_model=TaskMeJoinOutput,
               responses={
                   status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
               )
async def tasks_user_join(
        request: Request,
        pid: str = Path(..., description='project id'),
        task_id: str = Path(..., description='task id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TaskMeJoinOutput:
    ''' Join or remove to/from the task

    - **pid**: project id
    - **task_id**: task id

    '''
    # pylint: disable=too-many-branches
    project = Project.get(pid=pid)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task_data = Tasks.get_with_pid(pid=pid, _id=task_id)
    if not task_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return TaskMeJoinOutput(is_joined=current_user['uid'] in task_data['people'])

    if request.method == 'POST':
        Tasks.join(pid=pid, task_id=task_id, uid=current_user['uid'])
        return TaskMeJoinOutput(is_joined=True)

    if request.method == 'DELETE':
        Tasks.cancel(pid=pid, task_id=task_id, uid=current_user['uid'])
        return TaskMeJoinOutput(is_joined=False)

    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)


@router.get('/{pid}/{task_id}/attendee/list',
            summary='Get users to the task (get)',
            response_model=TaskGetAttendeeOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            )
@router.patch('/{pid}/{task_id}/attendee/list',
              summary='Add users to the task (update)',
              responses={
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
              response_model_exclude_none=True,
              )
@router.delete('/{pid}/{task_id}/attendee/list',
               summary='Remove users from the task (remove)',
               responses={
                   status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
               response_model_exclude_none=True,
               )
async def tasks_users_add(
        request: Request,
        update_data: TaskAttendeeInput | None = None,
        pid: str = Path(..., description='project id'),
        task_id: str = Path(..., description='task id'),
        current_user: dict[str, Any] = Depends(  # pylint: disable=unused-argument
            get_current_user)) -> TaskGetAttendeeOutput | None:
    ''' Add / Remove users to/from the task

    - **pid**: project id
    - **task_id**: task id

    '''
    # pylint: disable=too-many-branches
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

    if request.method == 'GET':
        result: list[UserItem] = []
        if task_data['people']:
            user_infos = User.get_info(uids=task_data['people'])
            if user_infos:
                for uid in task_data['people']:
                    if uid in user_infos:
                        result.append(UserItem.parse_obj({
                            'id': uid,
                            'badge_name': user_infos[uid]['profile']['badge_name'],
                            'avatar': user_infos[uid]['oauth']['picture'],
                        }))

        return TaskGetAttendeeOutput.parse_obj({'datas': result})

    if update_data is not None:
        if request.method == 'PATCH':
            user_infos = User.get_info(uids=update_data.uids)
            if user_infos:
                for uid in user_infos:
                    Tasks.join(pid=pid, task_id=task_id, uid=uid)
                return None

        if request.method == 'DELETE':
            for uid in update_data.uids:
                Tasks.cancel(pid=pid, task_id=task_id, uid=uid)
            return None

    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE)
