''' API Structs - Users '''
from datetime import date
from typing import Any

from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

from structs.users import UserBank


class UserMeOut(BaseModel):
    ''' UserMeOut '''
    uid: str = Field(description='user id')
    badge_name: str = Field(description='badge name')
    avatar: HttpUrl = Field(description='url for avatar')
    intro: str = Field(description='introduction')


class ProjectItem(BaseModel):
    ''' ProjectItem '''
    id: str = Field(description='`pid`, project id')
    name: str = Field(description='project name')
    desc: str | None = Field(description='desc')
    action_date: date | None = Field(description='action date')
    owners: list[str] | None = Field(description='list of owners')
    calendar: HttpUrl | None = Field(description='calendar url')
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
    volunteer_certificate_hours: int | None = Field(
        description='hours for volunteer certificate')

    @validator('*', pre=True)
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


class UserMeParticipatedItem(BaseModel):
    ''' UserMeParticipatedItem '''
    project: ProjectItem = Field(description='project')
    team: TeamItem = Field(description='team')
    action: date = Field(description='action date')
    title: str = Field(default='', description='title')


class UserMeParticipatedOut(BaseModel):
    ''' UserMeParticipatedOut '''
    datas: list[UserMeParticipatedItem] = Field(
        description='list of data sorted by action date',
        default=[],
    )


class UserMeBankOut(BaseModel):
    ''' UserMeBankOut '''
    bank: UserBank = Field(description='User bank info')
