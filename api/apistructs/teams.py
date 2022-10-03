''' API Structs - Teams '''
from pydantic import BaseModel, Field


class TeamItem(BaseModel):
    ''' TeamItem '''
    pid: str = Field(description='`pid`, project id')
    id: str = Field(description='`tid`, team id', alias='tid')
    name: str = Field(description='team name')
    chiefs: list[str] | None = Field(description="list of chiefs' uids")
    members: list[str] | None = Field(description="list of members' uids")
    desc: str | None = Field(description='desc')
