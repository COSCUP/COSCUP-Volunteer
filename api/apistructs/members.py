''' API Structs - Members '''
from pydantic import BaseModel, Field


class MembersInfo(BaseModel):
    ''' MembersInfo '''
    name: str = Field(description='User name or display name')
    email_hash: str = Field(description='Email hashed in MD5')


class MembersTeams(BaseModel):
    ''' MembersTeams '''
    name: str = Field(description='Team name')
    tid: str = Field(description='Team id')
    chiefs: list[MembersInfo] = Field(default=[], description='All chiefs')
    members: list[MembersInfo] = Field(default=[], description='All members')


class MembersOut(BaseModel):
    ''' MembersOut '''
    data: list[MembersTeams] = Field(default=[], description='All teams info.')
