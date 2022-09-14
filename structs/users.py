''' User Structs '''
from datetime import date
from time import time
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from module.dietary_habit import DietaryHabitItemsValue


class UserProfle(BaseModel):
    ''' User Profile struct

    Attributes:
        badge_name: Badge name.
        intro: introduction.

    '''
    badge_name: str = Field(..., example='Badge Name')
    intro: str = Field(default='')


class UserBank(BaseModel):
    ''' User Bank info

    Attributes:
        code: bank code.
        no: bank account numbers.
        branch: bank branch name.
        name: bank account name.

    '''
    code: str = Field(default='')
    no: str = Field(default='')
    branch: str = Field(default='')
    name: str = Field(default='')


class UserAddress(BaseModel):
    ''' User Address

    Attributes:
        code: postal code.
        receiver: receiver name.
        address: address.

    '''
    code: str = Field(default='')
    receiver: str = Field(default='')
    address: str = Field(default='')


class UserProfleReal(BaseModel):
    ''' User Profile Real struct

    Attributes:
        name: name.
        phone: phone numbers.
        roc_id: user national id.
        company: company or school name.
        birthday: *(optional)* birthday.
        bank: *(optional)* bank info.
        address: *(optional)* address info.
        dietary_habit: *(optional)* dietary habit info.

    '''
    name: str = Field(default='')
    phone: str = Field(default='')
    roc_id: str = Field(default='')
    company: str = Field(default='')
    birthday: Optional[date] = Field(...)
    bank: Optional[UserBank]
    address: Optional[UserAddress]
    dietary_habit: Optional[list[DietaryHabitItemsValue]]

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            use_enum_values: `True`

        '''
        use_enum_values: bool = True


class User(BaseModel):
    ''' User struct

    Attributes:
        id: user id. *(alias: `_id`)*
        created_at: timestamp.
        mail: mail.
        profile: profile info.
        profile_real: real profile info.

    !!! TODO

        Need to convert the `int` type to `datetime` of `created_at`.

    '''
    id: str = Field(..., alias='_id')
    created_at: int = Field(default_factory=lambda: int(time()))
    mail: EmailStr = Field(..., description="User's mail")
    profile: Optional[UserProfle]
    profile_real: Optional[UserProfleReal]
