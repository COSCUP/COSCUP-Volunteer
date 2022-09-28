''' API Structs - Users '''
from datetime import date

from pydantic import BaseModel, Field, HttpUrl


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
