''' User Structs '''
from datetime import datetime
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

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


class UserBank(BaseModel):
    ''' User Bank info

    Attributes:
        code: bank code.
        no: bank account numbers.
        branch: bank branch name.
        name: bank account name.

    '''
    code: str = Field(default='', description='bank code')
    no: str = Field(default='', description='bank account numbers')
    branch: str = Field(default='', description='bank branch name')
    name: str = Field(default='', description='bank account name')

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


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

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True


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
    birthday: Optional[datetime]
    bank: Optional[UserBank] = Field(default_factory=UserBank)
    address: Optional[UserAddress] = Field(default_factory=UserAddress)
    dietary_habit: Optional[list[DietaryHabitItemsValue]] = Field(
        default_factory=list)

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`
            use_enum_values: `True`

        '''
        anystr_strip_whitespace: bool = True
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

    class Config:  # pylint: disable=too-few-public-methods
        ''' Config

        Attributes:
            anystr_strip_whitespace: `True`

        '''
        anystr_strip_whitespace: bool = True
