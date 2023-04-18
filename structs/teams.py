''' Teams Structs '''
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, validator


class TagMembers(BaseModel):
    ''' TagMembers '''
    id: str = Field(description='random id')
    name: str = Field(description='tag name')


class TeamBase(BaseModel):
    ''' TeamBase '''
    id: str = Field(description='`tid`, team id', alias='tid')
    pid: str = Field(description='`pid`, project id')
    name: str = Field(description='team name')
    owners: list[str] | None = Field(description="list of owners' uids")
    chiefs: list[str] | None = Field(description="list of chiefs' uids")
    members: list[str] | None = Field(description="list of members' uids")
    desc: str | None = Field(description='desc')
    mailling: EmailStr | None = Field(description='mailing list for team')
    headcount: int | None = Field(description='the headcount of team')
    public_desc: str | None = Field(description='public desc for not members')
    disabled: bool = Field(default=False, description='disabled the team')
    tag_members: list[TagMembers] | None = Field(
        description='tags for members')
    created_at: datetime | None = Field(description='create at')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config '''
        anystr_strip_whitespace = True


class TeamUsers(BaseModel):
    ''' Default list type for owners, chiefs, members '''
    owners: list[str] = Field(default_factory=list,
                              description="list of owners' uids")
    chiefs: list[str] = Field(default_factory=list,
                              description="list of chiefs' uids")
    members: list[str] = Field(
        default_factory=list, description="list of members' uids")

    @validator('*', pre=True)
    def process_none(cls, value: list[str] | None) -> list[str]:  # pylint: disable=no-self-argument
        ''' process none '''
        if value is None:
            return []

        return value


class TeamApplyReviewMessage(BaseModel):
    ''' Team apply review message '''
    role: str
    content: str


class TeamApplyReview(BaseModel):
    ''' Team apply review '''
    pid: str = Field(description='`pid`, project id')
    tid: str = Field(description='`tid`, team id')
    uid: str = Field(description='`uid`, user id')
    messages: list[TeamApplyReviewMessage] = Field(
        description='list results', default_factory=list)
