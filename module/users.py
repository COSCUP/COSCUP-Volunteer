''' users '''
from typing import Any, Generator, Optional

from pymongo.collection import ReturnDocument

from models.oauth_db import OAuthDB
from models.users_db import TobeVolunteerDB, UsersDB
from module.skill import TobeVolunteerStruct
from structs.users import UserBank, UserProfle


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
    def get(uid: str) -> dict[str, Any]:
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

        return TobeVolunteerStruct.parse_obj(data).dict()

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
