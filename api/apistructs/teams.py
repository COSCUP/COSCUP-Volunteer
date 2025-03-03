''' API Structs - Teams '''
from typing import Any

from pydantic import field_validator, ConfigDict, BaseModel, EmailStr, Field

from api.apistructs.items import UserItem


class TeamItemUpdateInput(BaseModel):
    ''' Update Team item input '''
    name: str | None = Field(None, description='team name')
    desc: str | None = Field(None, description='desc')
    mailling: EmailStr | None = Field(None, description='mailing list for team')
    headcount: int | None = Field(None, description='the headcount of team')

    @field_validator('*', mode="before")
    @classmethod
    def skip_empty_str(cls, value: Any) -> Any:  # pylint:disable=no-self-argument
        ''' skip empty string '''
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None

        return value


class TeamItemUpdateOutput(TeamItemUpdateInput):
    ''' Update Team item output '''


class TeamAddressBookOutput(BaseModel):
    ''' Team address book output '''
    datas: list[UserItem] = Field(description='list of users info')


class TeamCreateInput(BaseModel):
    ''' Team create input '''
    id: str = Field(description='team id')
    name: str = Field(description='team name')
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamCreateOutput(TeamCreateInput):
    ''' TeamCreateOutput '''


class TeamUpdateMembers(BaseModel):
    ''' TeamUpdateMembers '''
    uids: list[str] = Field(description='uids')
    model_config = ConfigDict(str_strip_whitespace=True)


class TeamUpdateMembersOutput(BaseModel):
    ''' TeamUpdateMembersOutput '''
    status: bool = Field(default=False, description='output status')


class TeamGetVolunteersOutput(BaseModel):
    ''' TeamGetVolunteersOutput '''
    datas: list[UserItem] = Field(
        default_factory=list, description='list of users')
