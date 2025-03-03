''' API Structs - Tasks '''
from datetime import datetime

from pydantic import ConfigDict, BaseModel, Field

from api.apistructs.items import UserItem
from structs.tasks import TaskItem


class TasksGetAllOutput(BaseModel):
    ''' TasksGetAllOutput '''
    datas: list[TaskItem] = Field(
        default_factory=list, description='list of tasks')


class TaskCreateInput(BaseModel):
    ''' TaskItem '''
    title: str = Field(description='title')
    cate: str = Field(description='cate')
    desc: str = Field(description='desc')
    starttime: datetime = Field(
        default_factory=datetime.now, description='task start')
    endtime: datetime = Field(
        default_factory=datetime.now, description='task end')
    limit: int = Field(default=1, ge=1, description='expect required users')
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


class TaskCreateOutput(TaskItem):
    ''' TaskCreateOutput '''


class TaskGetOutput(TaskItem):
    ''' TaskGetOutput '''


class TaskUpdateInput(BaseModel):
    ''' TaskUpdateInput '''
    title: str | None = Field(None, description='title')
    cate: str | None = Field(None, description='cate')
    desc: str | None = Field(None, description='desc')
    starttime: datetime | None = Field(None, description='task start')
    endtime: datetime | None = Field(None, description='task end')
    limit: int | None = Field(None, description='expect required users')
    model_config = ConfigDict(str_strip_whitespace=True)


class TaskAttendeeInput(BaseModel):
    ''' TaskAttendeeInput '''
    uids: list[str] = Field(description='uids')
    model_config = ConfigDict(str_strip_whitespace=True)


class TaskGetAttendeeOutput(BaseModel):
    ''' TaskAttendeeInput '''
    datas: list[UserItem] = Field(description='list of attendee')


class TaskMeJoinOutput(BaseModel):
    ''' TaskMeJoinOutput '''
    is_joined: bool = Field(default=False, description='joined or not')
