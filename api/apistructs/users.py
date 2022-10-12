''' API Structs - Users '''
from datetime import date

from pydantic import BaseModel, Field, HttpUrl

from api.apistructs.items import ProjectItem, TeamItem
from module.skill import SkillEnum, StatusEnum, TeamsEnum, TobeVolunteerStruct
from structs.users import UserAddress, UserBank, UserProfle, UserProfleRealBase


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


class UserMeBankInput(UserBank):
    ''' UserMeBankInput '''


class UserMeBankOut(UserBank):
    ''' UserMeBankOut '''


class UserMeProfileInput(UserProfle):
    ''' UserMeProfileInput '''


class UserMeProfileOutput(UserProfle):
    ''' UserMeProfileOutput '''


class UserMeAddressInput(UserAddress):
    ''' UserMeAddressInput '''


class UserMeAddressOutput(UserAddress):
    ''' UserMeAddressOutput '''


class UserMeProfileRealInput(UserProfleRealBase):
    ''' UserMeProfileRealInput '''


class UserMeProfileRealOutput(UserProfleRealBase):
    ''' UserMeProfileRealOutput '''


class UserMeDietaryHabitItem(BaseModel):
    ''' UserMeDietaryHabitItem '''
    name: str = Field(description='code')
    value: str = Field(description='in chinese name')
    checked: bool = Field(default=False, description='user selected')


class UserMeDietaryHabitInput(BaseModel):
    ''' UserMeDietaryHabitInput '''
    checked: list[str] = Field(
        description='lists value of `DietaryHabitItemsValue`',
        example=['0.001', '0.002'],
    )


class UserMeDietaryHabitOutput(BaseModel):
    ''' UserMeDietaryHabitOutput '''
    data: list[UserMeDietaryHabitItem] = Field(
        description='lists of dietary habit items')


class UserMeToBeVolunteerOptionItem(BaseModel):
    ''' UserMeToBeVolunteerOptionItem '''
    code: str
    desc: str


class UserMeToBeVolunteerOptionStrItem(UserMeToBeVolunteerOptionItem):
    ''' UserMeToBeVolunteerOptionStrItem '''
    value: str


class UserMeToBeVolunteerOptionIntItem(UserMeToBeVolunteerOptionItem):
    ''' UserMeToBeVolunteerOptionIntItem '''
    value: int


class UserMeToBeVolunteerOptionsOutput(BaseModel):
    ''' UserMeToBeVolunteerOptionsOutput '''
    teams: list[UserMeToBeVolunteerOptionIntItem]
    skills: list[UserMeToBeVolunteerOptionStrItem]
    status: list[UserMeToBeVolunteerOptionIntItem]


class UserMeToBeVolunteerInput(BaseModel):
    ''' UserMeToBeVolunteerOutput '''
    ok: bool = Field(default=False, description='ok to be volunteer')
    teams: list[TeamsEnum] = Field(description='list of teams')
    skill: list[SkillEnum] = Field(description='list of skills')
    hours: int = Field(description='Hours in an week')
    status: StatusEnum = Field(description='status')
    desc: str = Field(default='', description='more description')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config '''
        anystr_strip_whitespace: bool = True
        use_enum_values: bool = True


class UserMeToBeVolunteerOutput(BaseModel):
    ''' UserMeToBeVolunteerOutput '''
    data: TobeVolunteerStruct = Field(description='to be volunteer data')
