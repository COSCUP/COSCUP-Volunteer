''' API Structs - Projects '''
from datetime import date, datetime

import arrow
from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator

from api.apistructs.items import ProjectItem, TeamItem
from structs.projects import ProjectTrafficLocationFeeItem


class ProjectAllOut(BaseModel):
    ''' ProjectAllOut '''
    datas: list[ProjectItem] = Field(
        default=[], description='list of projects')


class ProjectCreate(BaseModel):
    ''' Project create input '''
    name: str = Field(description='project name')
    action_date: str = Field(description='Date format in YYYY/MM/DD')


class ProjectCreateInput(ProjectCreate):
    ''' Project create input '''
    pid: str = Field(description='project id')


class ProjectCreateOutput(ProjectCreate):
    ''' Project create output '''
    pid: str = Field(description='project id', alias='_id')

    @validator('action_date', pre=True)
    def convert_action_date(cls, value: datetime) -> str:  # pylint: disable=no-self-argument
        ''' convert_action_date '''
        return arrow.get(value).format('YYYY/MM/DD')


class ProjectItemUpdateInput(BaseModel):
    ''' Update project item input '''
    name: str | None = Field(description='project name')
    desc: str | None = Field(description='desc')
    action_date: date | None = Field(description='action date')
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
    volunteer_certificate_hours: int | None = Field(
        description='hours for volunteer certificate')


class ProjectItemUpdateOutput(ProjectItemUpdateInput):
    ''' Update project item output '''

    @validator('action_date', pre=True)
    def convert_action_date(cls, value: str | int | float) -> date:  # pylint:disable=no-self-argument
        ''' convert action_date to date '''
        return arrow.get(value).date()


class ProjectTeamsOutput(BaseModel):
    ''' List of teams in project '''
    teams: list[TeamItem]


class ProjectTeamDietaryHabitOutput(BaseModel):
    ''' List of the statistics of dietary habit '''
    name: str = Field(description='name of dietary habit')
    count: int = Field(description='counts')
    code: str = Field(description='internal code')


class ProjectSettingTrafficSubsidyOutput(BaseModel):
    ''' List of the traffic subsidy '''
    datas: list[ProjectTrafficLocationFeeItem] = Field(
        default_factory=list, description='list of datas')


class ProjectSettingTrafficSubsidyInput(BaseModel):
    ''' List of the traffic subsidy input '''
    datas: list[ProjectTrafficLocationFeeItem] = Field(
        description='list of datas')
