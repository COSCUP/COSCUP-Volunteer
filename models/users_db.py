''' User database '''
from time import time
from typing import Any
from uuid import uuid4

from pymongo.collection import ReturnDocument
from pymongo.results import InsertOneResult

from models.base import DBBase
from structs.users import PolicyType, PolicySigned


class UsersDB(DBBase):  # pylint: disable=abstract-method
    ''' UsersDB Collection '''

    def __init__(self) -> None:
        super().__init__('users')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `mail`
            - `property.suspend`

        '''
        self.create_index([('mail', 1), ])
        self.create_index([('property.suspend', 1), ])

    @staticmethod
    def new(mail: str) -> dict[str, Any]:
        ''' New user account

        Args:
            mail (str): Mail address.

        Returns:
            Return the user base object and the `_id` it will be the user id.

        TODO:
            ``mail`` bind to login oauth account. Maybe need ``alias`` for
            some case like one user have more mail account to register.

        '''
        return {
            '_id': f'{uuid4().fields[0]:08x}',
            'mail': mail,
            'created_at': int(time()),
        }

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add data

        Args:
            data (dict): The data to insert / update.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


class TobeVolunteerDB(DBBase):  # pylint: disable=abstract-method
    ''' TobeVolunteer Collection '''

    def __init__(self) -> None:
        super().__init__('tobe_volunteer')

    def add(self, data: dict[str, Any]) -> None:
        ''' add

        Args:
            data (dict): The data to insert / update.

        '''
        self.find_one_and_update(
            {'_id': data['uid']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


class PolicySignedDB(DBBase):
    ''' PolicySigned Collection '''

    def __init__(self) -> None:
        super().__init__('policy_signed')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `type`, `sign_at`

        '''
        self.create_index([('type', 1), ('sign_at', -1), ])

    def save(self, uid: str, _type: PolicyType) -> InsertOneResult:
        ''' Save the signed data

        Args:
            uid (str): user id
            _type (PolicyType): Ploicy type

        '''
        return self.insert_one(PolicySigned(uid=uid, type=_type).dict())
