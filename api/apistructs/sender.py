''' API Structs - Sender '''
from datetime import datetime
from typing import Any

import arrow
from pydantic import BaseModel, Field, validator


class SenderCampaignInput(BaseModel):
    ''' Sender campaign input '''
    name: str = Field(description='name')


class Creater(BaseModel):
    ''' Creater '''
    pid: str = Field(description='project id')
    tid: str = Field(description='team id')
    uid: str = Field(description='user id')
    at: datetime = Field(description='created at in timestamp')

    @validator('at', pre=True)
    def convert_to_datetime(cls, value: int | float | datetime) -> datetime:  # pylint: disable=no-self-argument
        ''' convert to datetime '''
        return arrow.get(value).naive


class TeamTagsItem(BaseModel):
    ''' Team tags item '''
    tid: str = Field(description='team id')
    tags: list[str] = Field(description='tag ids')


class Receiver(BaseModel):
    ''' Receiver '''
    teams: list[str] = Field(default_factory=list,
                             description='lists of `tid`')
    users: list[str] = Field(default_factory=list,
                             description='lists of `uid`')
    team_w_tags: list[TeamTagsItem] = Field(
        default_factory=list, description='lists of team/tags')
    all_users: bool = Field(
        default=False, description='Send to all users in platform')

    @validator('team_w_tags', pre=True)
    def convert_to_list(cls,  # pylint: disable=no-self-argument
                        value: Any | list[dict[str, str | list[str]]]) -> list[
            dict[str, str | list[str]]]:
        ''' convert to list '''
        if isinstance(value, dict):
            result = []
            for tid, tags in value.items():
                result.append({'tid': tid, 'tags': tags})

            return result

        return value


class Mail(BaseModel):
    ''' Mail '''
    subject: str = Field(default='', description='mail subject')
    content: str = Field(default='', description='mail content')
    preheader: str = Field(default='', description='mail preheader')
    layout: str = Field(default='', description='mail layout')


class CampaignItem(BaseModel):
    ''' Campaign item '''
    id: str = Field(description='campaign id', alias='_id')
    name: str = Field(description='name')
    creater: Creater = Field(description='creater info', alias='created')
    receiver: Receiver = Field(description='receiver info')
    mail: Mail = Field(description='mail content')


class SenderCampaignLists(BaseModel):
    ''' Sender campaign lists '''
    datas: list[CampaignItem] = Field(description='lists of campaigns')
