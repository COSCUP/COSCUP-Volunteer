''' API Structs - Projects '''
from datetime import date

import arrow
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

from api.apistructs.items import ProjectItem, TeamItem


class ProjectAllOut(BaseModel):
    ''' ProjectAllOut '''
    datas: list[ProjectItem] = Field(
        default=[], description='list of projects')


class ProjectItemUpdateInput(BaseModel):
    ''' Update project item input '''
    name: str | None = Field(description='project name')
    desc: str | None = Field(description='desc')
    action_date: date | None = Field(description='action date')
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


class ProjectItemUpdateOutput(ProjectItemUpdateInput):
    ''' Update project item output '''

    @validator('action_date', pre=True)
    def convert_action_date(cls, value: str | int) -> date:  # pylint:disable=no-self-argument
        ''' convert action_date to date '''
        return arrow.get(value).date()


class ProjectTeamsOutput(BaseModel):
    ''' List of teams in project '''
    teams: list[TeamItem]
