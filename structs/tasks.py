''' Tasks Structs '''
from datetime import datetime
from typing import Any
from uuid import uuid4

import arrow
from pydantic import BaseModel, ConfigDict, Field, field_validator


def convert_datetime(value: Any) -> datetime:
    ''' convert `action_date` to date '''
    return arrow.get(value).naive


def gen_uuid() -> str:
    ''' gen_uuid '''
    return f'{uuid4().fields[0]:08x}'


class TaskItem(BaseModel):
    ''' TaskItem '''
    id: str = Field(description='task id',
                    default_factory=gen_uuid, alias='_id')
    pid: str = Field(description='project id')
    title: str = Field(default='', description='title')
    cate: str = Field(default='', description='cate')
    created_at: datetime = Field(
        default_factory=datetime.now, description='created at')
    created_by: str = Field(description='created by')
    desc: str = Field(description='desc')
    starttime: datetime = Field(
        default_factory=datetime.now, description='task start')
    endtime: datetime = Field(
        default_factory=datetime.now, description='task end')
    limit: int = Field(default=1, ge=1, description='expect required users')
    people: list[str] = Field(default_factory=list,
                              description='list of users')

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True)

    @field_validator("created_at", "starttime", "endtime", mode="before")
    @classmethod
    def valid_convert_action_date(cls, value: Any) -> Any:
        ''' convert `action_date` to date '''
        return convert_datetime(value=value)
