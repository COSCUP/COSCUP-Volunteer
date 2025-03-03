''' Teams Structs '''
from datetime import datetime

from pydantic import field_validator, ConfigDict, BaseModel, EmailStr, Field


class TagMembers(BaseModel):
    ''' TagMembers '''
    id: str = Field(description='random id')
    name: str = Field(description='tag name')


class TeamBase(BaseModel):
    ''' TeamBase '''
    id: str = Field(description='`tid`, team id', alias='tid')
    pid: str = Field(description='`pid`, project id')
    name: str = Field(description='team name')
    owners: list[str] | None = Field(None, description="list of owners' uids")
    chiefs: list[str] | None = Field(None, description="list of chiefs' uids")
    members: list[str] | None = Field(None, description="list of members' uids")
    desc: str | None = Field(None, description='desc')
    mailling: EmailStr | None = Field(None, description='mailing list for team')
    headcount: int | None = Field(None, description='the headcount of team')
    public_desc: str | None = Field(None, description='public desc for not members')
    disabled: bool = Field(default=False, description='disabled the team')
    tag_members: list[TagMembers] | None = Field(
        None, description='tags for members')
    created_at: datetime | None = Field(None, description='create at')
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamUsers(BaseModel):
    ''' Default list type for owners, chiefs, members '''
    owners: list[str] = Field(default_factory=list,
                              description="list of owners' uids")
    chiefs: list[str] = Field(default_factory=list,
                              description="list of chiefs' uids")
    members: list[str] = Field(
        default_factory=list, description="list of members' uids")

    @field_validator('*', mode="before")
    @classmethod
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
