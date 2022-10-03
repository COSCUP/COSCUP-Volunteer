''' API Structs - Users '''
from datetime import date

from pydantic import BaseModel, Field, HttpUrl

from api.apistructs.projects import ProjectItem
from api.apistructs.teams import TeamItem
from structs.users import UserBank


class UserMeOut(BaseModel):
    ''' UserMeOut '''
    uid: str = Field(description='user id')
    badge_name: str = Field(description='badge name')
    avatar: HttpUrl = Field(description='url for avatar')
    intro: str = Field(description='introduction')


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
