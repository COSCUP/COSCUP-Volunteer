''' API Structs - Projects '''
from datetime import date, datetime

import arrow
from pydantic import field_validator, BaseModel, EmailStr, Field, HttpUrl

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

    @field_validator('action_date', mode="before")
    @classmethod
    def convert_action_date(cls, value: datetime) -> str:  # pylint: disable=no-self-argument
        ''' convert_action_date '''
        return arrow.get(value).format('YYYY/MM/DD')


class ProjectItemUpdateInput(BaseModel):
    ''' Update project item input '''
    name: str | None = Field(None, description='project name')
    desc: str | None = Field(None, description='desc')
    action_date: date | None = Field(None, description='action date')
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


class ProjectItemUpdateOutput(ProjectItemUpdateInput):
    ''' Update project item output '''

    @field_validator('action_date', mode="before")
    @classmethod
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
