''' Project Structs '''
from datetime import date, datetime
from typing import Any

import arrow
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator


def skip_empty_str(value: Any) -> Any:
    ''' skip empty string '''
    if isinstance(value, str):
        value = value.strip()

    if not value:
        return None

    return value


def convert_action_date(value: int | date | datetime | str) -> datetime:
    ''' convert `action_date` to date '''
    if isinstance(value, (int, date, str)):
        value = arrow.get(value).datetime

    return value


class ProjectBase(BaseModel):
    ''' ProjectBase'''
    id: str = Field(description='`pid`, project id', alias='_id')
    name: str = Field(description='project name')
    owners: list[str] = Field(description='list of owners')
    action_date: datetime = Field(description='action date')
    desc: str | None = Field(description='desc')
    calendar: str | None = Field(description='calendar url')
    gitlab_project_id: str | None = Field(description='gitlab project id')
    mailling_leader: EmailStr | None = Field(
        description='mailing list of leader')
    mailling_staff: EmailStr | None = Field(
        description='mailing list of staff')
    mattermost_ch_id: str | None = Field(
        description='Mattermost main channel id')
    shared_drive: HttpUrl | None = Field(description='Google shared drive')
    traffic_fee_doc: HttpUrl | None = Field(
        description='doc fields for traffic fee')
    volunteer_certificate_hours: int = Field(
        default=16, ge=0,
        description='hours for volunteer certificate')

    _validate_skip_empty_str = validator(
        '*', pre=True, allow_reuse=True)(skip_empty_str)
    _validate_convert_action_date = validator(
        'action_date', pre=True, allow_reuse=True)(convert_action_date)


class ProjectBaseUpdate(BaseModel):
    ''' ProjectBaseUpdate '''
    name: str | None = Field(description='project name')
    action_date: datetime | None = Field(description='action date')
    desc: str | None = Field(description='desc')
    calendar: str | None = Field(description='calendar url')
    gitlab_project_id: str | None = Field(description='gitlab project id')
    mailling_leader: EmailStr | None = Field(
        description='mailing list of leader')
    mailling_staff: EmailStr | None = Field(
        description='mailing list of staff')
    mattermost_ch_id: str | None = Field(
        description='Mattermost main channel id')
    shared_drive: HttpUrl | None = Field(description='Google shared drive')
    traffic_fee_doc: HttpUrl | None = Field(
        description='doc fields for traffic fee')
    volunteer_certificate_hours: int = Field(
        default=16, ge=0,
        description='hours for volunteer certificate')

    _validate_skip_empty_str = validator(
        '*', pre=True, allow_reuse=True)(skip_empty_str)
    _validate_convert_action_date = validator(
        'action_date', pre=True, allow_reuse=True)(convert_action_date)
