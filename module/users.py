''' users '''
from typing import Any, Generator, Optional

import arrow
from pydantic import BaseModel, Field, parse_obj_as
from pymongo.collection import ReturnDocument

from models.oauth_db import OAuthDB
from models.users_db import PolicySignedDB, TobeVolunteerDB, UsersDB
from module.dietary_habit import DietaryHabitItemsValue
from module.mattermost_bot import MattermostTools
from module.skill import TobeVolunteerStruct
from structs.users import PolicyType
from structs.users import User as UserStruct
from structs.users import UserAddress, UserBank, UserProfle, UserProfleRealBase


class User:
    ''' User

    Args:
        uid (str): User id.
        mail (str): User mail.

    '''

    def __init__(self, uid: Optional[str] = None, mail: Optional[str] = None) -> None:
        self.uid = uid
        self.mail = mail

    def get(self) -> Optional[dict[str, Any]]:
        ''' Get user data

        Returns:
            Return user info.

        '''
        return UsersDB().find_one({'$or': [{'_id': self.uid}, {'mail': self.mail}]})

    @staticmethod
    def create(mail: str, force: bool = False) -> dict[str, Any]:
        ''' create user

        Args:
            mail (str): User mail.
            force (bool): Force to create.

        Returns:
            Return the created data.

        '''
        if not force:
            oauth_data = OAuthDB().find_one({'_id': mail}, {'owner': 1})
            if oauth_data is None:
                raise Exception(f'mail: `{mail}` not in the oauth dbs')

            if 'owner' in oauth_data and oauth_data['owner']:
                raise Exception(f'mail:`{mail}` already bind')

        user = UsersDB().add(UsersDB.new(mail=mail))
        OAuthDB().setup_owner(mail=user['mail'], uid=user['_id'])

        return user

    def get_profile(self) -> UserProfle | None:
        ''' Get user's profile

        Returns:
            Return the user profile data.

        '''
        for data in UsersDB().find({'_id': self.uid}, {'profile': 1}):
            if 'profile' in data:
                return UserProfle.parse_obj(data['profile'])

        return None

    def update_profile(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' update profile

        Args:
            data (dict): Profile data.

        Returns:
            Return the updated data.

        Bug:
            Need to verify and filter.

        '''
        return UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'profile': data}},
            return_document=ReturnDocument.AFTER,
        )

    def get_profile_real(self) -> UserProfleRealBase:
        ''' Get profile real

        Returns:
            Return the real profile of user

        '''
        for data in UsersDB().find({'_id': self.uid}, {'profile_real': 1}):
            if 'profile_real' in data:
                return UserProfleRealBase.parse_obj(data['profile_real'])

        return UserProfleRealBase()

    def update_profile_real_base(self, data: UserProfleRealBase) -> UserProfleRealBase:
        ''' update profile real base

        Args:
            data (UserProfleRealBase): Profile base data.

        Returns:
            Return the updated data.

        '''
        return UserProfleRealBase.parse_obj(UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {
                'profile_real.name': data.name,
                'profile_real.phone': data.phone,
                'profile_real.roc_id': data.roc_id,
                'profile_real.company': data.company,
            }},
            return_document=ReturnDocument.AFTER,
        )['profile_real'])

    def update_profile_real(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' update profile

        Args:
            data (dict): Profile data.

        Returns:
            Return the updated data.

        Bug:
            Need to verify and filter.

        '''
        return UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'profile_real': data}},
            return_document=ReturnDocument.AFTER,
        )

    def get_dietary_habit(self) -> list[DietaryHabitItemsValue]:
        ''' Get dietary habit

        Returns:
            Return the dietary habit of user

        '''
        result: list[DietaryHabitItemsValue] = []
        for data in UsersDB().find({'_id': self.uid}, {'profile_real.dietary_habit': 1}):
            if 'profile_real' in data and 'dietary_habit' in data['profile_real']:
                for die in data['profile_real']['dietary_habit']:
                    result.append(DietaryHabitItemsValue(die))

        return result

    def update_dietary_habit(self,
                             values: list[DietaryHabitItemsValue]) -> list[DietaryHabitItemsValue]:
        ''' Update dietary habit

        Returns:
            Return the dietary habit of user

        '''
        saved = UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'profile_real.dietary_habit': [
                value.value for value in values]}},
            return_document=ReturnDocument.AFTER,
        )

        return parse_obj_as(list[DietaryHabitItemsValue], saved['profile_real']['dietary_habit'])

    def property_suspend(self, value: bool = True) -> dict[str, Any]:
        ''' Property suspend

        Args:
            value (bool): suspend or not.

        Returns:
            Return the updated data.

        '''
        return UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'property.suspend': value}},
            return_document=ReturnDocument.AFTER,
        )

    def has_suspended(self) -> bool:
        ''' user has been suspended or not

        Returns:
            Return the user has been suspended or not.

        '''
        user_data = self.get()
        if not user_data:
            raise Exception('No account.')

        if 'property' in user_data and 'suspend' in user_data['property'] and \
                user_data['property']['suspend']:
            return True

        return False

    @staticmethod
    def get_info(uids: list[str], need_sensitive: bool = False) -> dict[str, Any]:
        ''' Get user info

        Args:
            uids (list): List of `uid`.
            need_sensitive (bool): Return sensitive data.

        Returns:
            Return the user data.

        TODO:
            Need refactor in pydantic.

        '''
        users = {}
        base_fields = {'profile': 1,
                       'profile_real.phone': 1,
                       'profile_real.name': 1,
                       'profile_real.dietary_habit': 1,
                       }

        if need_sensitive:
            base_fields['profile_real.roc_id'] = 1

        for user in UsersDB().find({'_id': {'$in': uids}}, base_fields):
            users[user['_id']] = user
            oauth_data = OAuthDB().find_one(
                {'owner': user['_id']},
                {'data.name': 1, 'data.picture': 1, 'data.email': 1},
            )

            if not oauth_data:
                raise Exception(f"no user's oauth: {user['_id']}")

            users[user['_id']]['oauth'] = {
                'name': oauth_data['data']['name'],
                'picture': oauth_data['data']['picture'],
                'email': oauth_data['data']['email'],
            }

            if 'profile' not in user:
                users[user['_id']]['profile'] = {
                    'badge_name': oauth_data['data']['name'],
                    'intro': '',
                }

            if users[user['_id']]['profile']['badge_name'].strip() == '':
                users[user['_id']]['profile']['badge_name'] = oauth_data['data']['name']

            if 'profile_real' not in user:
                users[user['_id']]['profile_real'] = {
                    'phone': '',
                    'name': '',
                }

        return users

    @staticmethod
    def get_bank(uid: str) -> UserBank:
        ''' Get bank info

        Args:
            uid (str): User id.

        Returns:
            Return the data.

        '''
        for user in UsersDB().find({'_id': uid}, {'profile_real.bank': 1}):
            if 'profile_real' in user and 'bank' in user['profile_real']:
                return UserBank.parse_obj(user['profile_real']['bank'])

        return UserBank()

    @staticmethod
    def update_bank(uid: str, data: UserBank) -> UserBank:
        ''' Update bank info

        Args:
            uid (str): User id.

        Returns:
            Return the data.

        '''
        result = UsersDB().find_one_and_update(
            {'_id': uid},
            {'$set': {'profile_real.bank': data.dict()}},
            return_document=ReturnDocument.AFTER,
        )

        return UserBank.parse_obj(result['profile_real']['bank'])

    @staticmethod
    def get_address(uid: str) -> dict[str, Any]:
        ''' Get Address

        Args:
            uid (str): User id.

        Returns:
            Return the data.

        TODO:
            Need refactor in pydantic.

        '''
        address = {'code': '', 'receiver': '', 'address': ''}
        for user in UsersDB().find({'_id': uid}, {'profile_real.address': 1}):
            if 'profile_real' in user and 'address' in user['profile_real']:
                address.update(user['profile_real']['address'])

        return address

    @staticmethod
    def update_address(uid: str, data: UserAddress) -> UserAddress:
        ''' Update address info

        Args:
            uid (str): User id.

        Returns:
            Return the data.

        '''
        result = UsersDB().find_one_and_update(
            {'_id': uid},
            {'$set': {'profile_real.address': data.dict()}},
            return_document=ReturnDocument.AFTER,
        )

        return UserAddress.parse_obj(result['profile_real']['address'])

    @staticmethod
    def get_suspend_uids(uids: list[str]) -> Generator[dict[str, Any], None, None]:
        ''' Get suspend user's uids

        Args:
            uids (list): List of `uid`.

        Yields:
            Return all user's uids

        '''
        for row in UsersDB().find({
            '_id': {'$in': uids},
            'property.suspend': True,
        }, {'_id': 1}):
            yield row

    @staticmethod
    def get_all_users(include_suspend: bool = False) -> Generator[dict[str, Any], None, None]:
        ''' Get all users

        Args:
            include_suspend (bool): Include suspend.

        Yields:
            Return all users datas.

        '''
        query = {}
        if not include_suspend:
            query = {
                '$or': [
                    {'property.suspend': {'$exists': False}},
                    {'property.suspend': False},
                ]}

        for row in UsersDB().find(query, {'_id': 1}):
            yield row

    @staticmethod
    def count(include_suspend: bool = False) -> int:
        ''' Count users

        Args:
            include_suspend (bool): Include suspend.

        Returns:
            Count users.

        '''
        query = {}
        if not include_suspend:
            query = {
                '$or': [
                    {'property.suspend': {'$exists': False}},
                    {'property.suspend': False},
                ]}

        return UsersDB().count_documents(query)

    @staticmethod
    def marshal_dietary_habit(user_infos: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
        ''' marshel the dietary_habit from user's data

            Args:
                user_infos (dict): user datas from [User.get_info][module.users.User.get_info]

        '''
        for uid, user_info in user_infos.items():
            data = {
                'uid': uid,
                'name': user_info['profile']['badge_name'],
                'picture': user_info['oauth']['picture'],
                'dietary_habit': [],
            }

            if 'profile_real' in user_info and 'dietary_habit' in user_info['profile_real']:
                data['dietary_habit'] = user_info['profile_real']['dietary_habit']

            yield data


class TobeVolunteer:
    ''' TobeVolunteer '''
    @staticmethod
    def save(data: dict[str, Any]) -> None:
        ''' save

        Args:
            data (dict): The save data.

        Bug:
            Need to verify and filter.

        '''
        TobeVolunteerDB().add(data=data)

    @staticmethod
    def get(uid: str) -> TobeVolunteerStruct:
        ''' get data

        Args:
            uid (str): User id.

        Returns:
            Return the data.

        '''
        data = {}
        for item in TobeVolunteerDB().find({'_id': uid}):
            data.update(item)
            data['uid'] = data['_id']

        return TobeVolunteerStruct.parse_obj(data)

    @staticmethod
    def query(query: dict[str, Any]) -> Generator[dict[str, Any], None, None]:
        ''' query

        Args:
            query (dict): Query data

        Bug:
            Need to verify and filter.

        '''
        _query: dict[str, Any] = {'ok': True}
        _or: list[dict[str, Any]] = []

        if query['skill']:
            _or.append({'skill': {'$in': query['skill']}})

        if query['teams']:
            _or.append({'teams': {'$in': query['teams']}})

        if query['status']:
            _or.append({'status': {'$in': query['status']}})

        if _or:
            _query['$or'] = _or

        for raw in TobeVolunteerDB().find(_query):
            yield raw


class PolicySigned:
    ''' Policy Signed '''
    @staticmethod
    def sign(uid: str, _type: PolicyType) -> None:
        ''' make sign for policy

        Args:
            uid (str): user name
            _type (PolicyType): Policy type

        '''
        PolicySignedDB().save(uid=uid, _type=_type)

    @staticmethod
    def is_recently_signed(uid: str, _type: PolicyType, days: int = 90) -> \
            Generator[dict[str, Any], None, None]:
        ''' is recently signed

        Args:
            uid (str): user name
            _type (PolicyType): Policy type
            days (int): last days

        '''
        sign_at = arrow.now().shift(days=days*-1).naive

        for raw in PolicySignedDB().find({
            'type': _type.value, 'uid': uid, 'sign_at': {'$gte': sign_at}
        }, {'_id': 0}):
            yield raw


class AccountPass(BaseModel):
    ''' Account Pass '''
    uid: str = Field(description='user id')
    is_profile: bool = Field(default=False, description='Profile is ok.')
    is_coc: bool = Field(default=False, description='COC read is ok.')
    is_security_guard: bool = Field(
        default=False, description='Security guard read is ok.')
    is_edu_account: bool = Field(default=False, description="edu account mail")
    has_chat: bool = Field(default=False, description="chat account is ready")

    def __init__(self, **data: Any):  # pylint: disable=no-self-argument
        ''' load user data '''
        super().__init__(**data)
        self.check_profile()
        self.check_signed_policy()
        self.check_has_chat_account()

    def check_profile(self, at_least: int = 200) -> None:
        ''' Check profile is ok

        Args:
            at_least (int): at least words

        '''
        user_data = UserStruct.parse_obj(User(uid=self.uid).get())
        if user_data is None:
            return None

        if user_data.mail.endswith('edu.tw'):
            self.is_edu_account = True

        if user_data.profile is not None and user_data.profile.intro:
            if len(user_data.profile.intro.strip()) > at_least and \
                    all((key in user_data.profile.intro for key in ('技能', '年度期待'))):
                self.is_profile = True

        return None

    def check_signed_policy(self) -> None:
        ''' check the policy signed '''
        for _ in PolicySigned.is_recently_signed(uid=self.uid, _type=PolicyType.COC):
            self.is_coc = True
            break

        for _ in PolicySigned.is_recently_signed(uid=self.uid, _type=PolicyType.SECURITY_GUARD):
            self.is_security_guard = True
            break

    def check_has_chat_account(self) -> None:
        ''' check has chat account '''
        if MattermostTools.find_possible_mid(uid=self.uid):
            self.has_chat = True
