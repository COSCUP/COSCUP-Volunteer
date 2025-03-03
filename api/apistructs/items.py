''' API Structs - Items '''

from datetime import date
from typing import Any

from pydantic import field_validator, BaseModel, EmailStr, Field, HttpUrl


class ProjectItem(BaseModel):
    ''' ProjectItem '''
    id: str = Field(description='`pid`, project id')
    name: str = Field(description='project name')
    desc: str | None = Field(None, description='desc')
    action_date: date | None = Field(None, description='action date')
    owners: list[str] | None = Field(None, description='list of owners')
    calendar: str | None = Field(None, description='calendar url')
    gitlab_project_id: str | None = Field(None, description='gitlab project id')
    mailling_leader: EmailStr | None = Field(
        None, description='mailing list of leader')
    mailling_staff: EmailStr | None = Field(
        None, description='mailing list of staff')
    mattermost_ch_id: str | None = Field(
        None, description='Mattermost main channel id')
    shared_drive: HttpUrl | None = Field(None, description='Google shared drive')
    traffic_fee_doc: HttpUrl | None = Field(
        None, description='doc fields for traffic fee')
    volunteer_certificate_hours: int | None = Field(
        None, description='hours for volunteer certificate')

    @field_validator('*', mode="before")
    @classmethod
    def skip_empty_str(cls, value: Any) -> Any:  # pylint:disable=no-self-argument
        ''' skip empty string '''
        if isinstance(value, str):
            value = value.strip()

        if not value:
            return None

        return value


class TeamItem(BaseModel):
    ''' TeamItem '''
    pid: str = Field(description='`pid`, project id')
    id: str = Field(description='`tid`, team id')
    name: str = Field(description='team name')
    chiefs: list[str] | None = Field(None, description="list of chiefs' uids")
    members: list[str] | None = Field(None, description="list of members' uids")
    desc: str | None = Field(None, description='desc')
    mailling: EmailStr | None = Field(None, description='mailing list for team')
    headcount: int | None = Field(None, description='the headcount of team')

    @field_validator('*', mode="before")
    @classmethod
    def skip_empty_str(cls, value: Any) -> Any:  # pylint:disable=no-self-argument
        ''' skip empty string '''
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

        return value


class MattermostAccount(BaseModel):
    ''' Mattermost Account '''
    mid: str = Field(description='mattermost account id')
    nickname: str = Field(description='nickname')


class UserItem(BaseModel):
    ''' User item '''
    id: str = Field(description='user id')
    badge_name: str = Field(description='badge name')
    avatar: HttpUrl = Field(description='url for avatar')
    intro: str | None = Field(None, description='introduction')
    chat: MattermostAccount | None = Field(None, description='Mattermost account')
    is_chief: bool | None = Field(None, description='is the chief in the team')
