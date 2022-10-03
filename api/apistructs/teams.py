''' API Structs - Teams '''
from typing import Any

from pydantic import BaseModel, EmailStr, Field, validator

from api.apistructs.items import UserItem


class TeamItemUpdateInput(BaseModel):
    ''' Update Team item input '''
    name: str = Field(description='team name')
    desc: str | None = Field(description='desc')
    mailling: EmailStr | None = Field(description='mailing list for team')
    headcount: int | None = Field(description='the headcount of team')

    @validator('*', pre=True)
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
