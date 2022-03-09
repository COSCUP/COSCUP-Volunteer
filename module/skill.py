''' skill '''
from enum import Enum, IntEnum, unique
from typing import List

from pydantic import BaseModel


@unique
class TeamsEnum(IntEnum):
    ''' TeamsEnum '''
    COORDINATOR = 1
    SECRETARY = 2
    PROGRAM = 3
    MARKETING = 4
    SPONSOR = 5
    IT = 6
    PHOTO = 7
    FINANCE = 8
    FIELD = 9
    STREAMING = 10
    DOCUMENTARY = 11


@unique
class TeamsEnumDesc(str, Enum):
    ''' TeamsEnum with desc '''
    COORDINATOR = '總召'
    SECRETARY = '行政'
    PROGRAM = '議程'
    MARKETING = '行銷'
    SPONSOR = '贊助'
    IT = '資訊'
    PHOTO = '攝影'
    FINANCE = '財務'
    FIELD = '場務'
    STREAMING = '製播'
    DOCUMENTARY = '紀錄'


@unique
class SkillEnum(str, Enum):
    ''' SkillEnum '''
    L001 = 'L001'
    L002 = 'L002'
    L003 = 'L003'
    L004 = 'L004'
    A001 = 'A001'
    S001 = 'S001'
    S002 = 'S002'
    S003 = 'S003'
    S004 = 'S004'
    S005 = 'S005'
    S006 = 'S006'
    O001 = 'O001'
    O002 = 'O002'
    O003 = 'O003'
    O004 = 'O004'
    O005 = 'O005'
    O006 = 'O006'
    O007 = 'O007'


@unique
class SkillEnumDesc(str, Enum):
    ''' SkillEnum with desc '''
    L001 = '語言：中文'
    L002 = '語言：臺語 / tâi-gí'
    L003 = '語言：英文'
    L004 = '語言：日本語'
    A001 = '企劃活動'
    S001 = '影片剪輯'
    S002 = '線上轉播導播'
    S003 = 'Podcast'
    S004 = '撰寫新聞稿'
    S005 = '精通 Adobe'
    S006 = 'A6 小冊子'
    O001 = '熱血'
    O002 = '助人'
    O003 = '力量'
    O004 = '喜愛站在講台上'
    O005 = '喜愛站在台下'
    O006 = '想事情的時候會看右邊'
    O007 = '想事情的時候會看左邊'


@unique
class StatusEnum(IntEnum):
    ''' StatusEnum '''
    ST01 = 1
    ST02 = 2
    ST03 = 3


@unique
class StatusEnumDesc(str, Enum):
    ''' StatusEnumDesc '''
    ST01 = '學生'
    ST02 = '工作'
    ST03 = '退休'


class TobeVolunteerStruct(BaseModel):
    ''' TobeVolunteer '''
    uid: str = ''
    ok: bool = False
    teams: List[TeamsEnum] = []
    skill: List[SkillEnum] = []
    hours: int = 0
    status: StatusEnum = 0
    desc: str = ''

    class Config:
        use_enum_values = True


class RecruitQuery(BaseModel):
    ''' RecruitQuery '''
    teams: List[TeamsEnum] = []
    skill: List[SkillEnum] = []
    status: List[StatusEnum] = []

    class Config:
        use_enum_values = True
