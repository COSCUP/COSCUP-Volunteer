import logging

from models.oauth_db import OAuthDB
from models.users_db import TobeVolunteerDB, UsersDB
from pymongo.collection import ReturnDocument

from module.skill import TobeVolunteerStruct


class User(object):
    ''' User

    :param str uid: user id
    :param str mail: mail

    '''

    def __init__(self, uid=None, mail=None):
        self.uid = uid
        self.mail = mail

    def get(self):
        ''' Get user data

        :rtype: dict

        '''
        return UsersDB().find_one({'$or': [{'_id': self.uid}, {'mail': self.mail}]})

    @staticmethod
    def create(mail, force=False):
        ''' create user

        :param str mail: mail
        :rtype: dict

        '''
        if not force:
            oauth_data = OAuthDB().find_one({'_id': mail}, {'owner': 1})
            if 'owner' in oauth_data and oauth_data['owner']:
                raise Exception('mail:`%s` already bind' % mail)

        user = UsersDB().add(UsersDB.new(mail=mail))
        OAuthDB().setup_owner(mail=user['mail'], uid=user['_id'])

        return user

    def update_profile(self, data):
        ''' update profile

        :param dict data: data

        '''
        return UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'profile': data}},
            return_document=ReturnDocument.AFTER,
        )

    def update_profile_real(self, data):
        ''' update profile

        :param dict data: data

        '''
        return UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'profile_real': data}},
            return_document=ReturnDocument.AFTER,
        )

    def property_suspend(self, value: bool = True) -> dict:
        ''' Property suspend '''
        return UsersDB().find_one_and_update(
            {'_id': self.uid},
            {'$set': {'property.suspend': value}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_info(uids, need_sensitive=False):
        ''' Get user info

        :param list uids: uid
        :param bool need_sensitive: show sensitive data

        '''
        users = {}
        base_fields = {'profile': 1,
                       'profile_real.phone': 1,
                       'profile_real.name': 1,
                       'profile_real.dietary_habit': 1,
                       }

        if need_sensitive:
            base_fields['profile_real.roc_id'] = 1

        for u in UsersDB().find({'_id': {'$in': uids}}, base_fields):
            users[u['_id']] = u
            oauth_data = OAuthDB().find_one(
                {'owner': u['_id']},
                {'data.name': 1, 'data.picture': 1, 'data.email': 1},
            )
            users[u['_id']]['oauth'] = {
                'name': oauth_data['data']['name'],
                'picture': oauth_data['data']['picture'],
                'email': oauth_data['data']['email'],
            }

            if 'profile' not in u:
                users[u['_id']]['profile'] = {
                    'badge_name': oauth_data['data']['name'],
                    'intro': '',
                }

            if 'profile_real' not in u:
                users[u['_id']]['profile_real'] = {
                    'phone': '',
                    'name': '',
                }

        return users

    @staticmethod
    def get_bank(uid):
        ''' Get bank info '''
        bank = {'code': '', 'no': '', 'branch': '', 'name': ''}
        for u in UsersDB().find({'_id': uid}, {'profile_real.bank': 1}):
            if 'profile_real' in u and 'bank' in u['profile_real']:
                bank.update(u['profile_real']['bank'])

        return bank

    @staticmethod
    def get_address(uid: str) -> dict:
        ''' Get Address '''
        address = {'code': '', 'receiver': '', 'address': ''}
        for user in UsersDB().find({'_id': uid}, {'profile_real.address': 1}):
            if 'profile_real' in user and 'address' in user['profile_real']:
                address.update(user['profile_real']['address'])

        return address

    @staticmethod
    def get_all_users(include_suspend: bool = False):
        ''' Get all users '''
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
    def count(include_suspend: bool = False):
        ''' Count users '''
        query = {}
        if not include_suspend:
            query = {
                '$or': [
                    {'property.suspend': {'$exists': False}},
                    {'property.suspend': False},
                ]}

        return UsersDB().count_documents(query)


class TobeVolunteer:
    ''' TobeVolunteer '''
    @staticmethod
    def save(data):
        ''' save '''
        TobeVolunteerDB().add(data=data)

    @staticmethod
    def get(uid):
        ''' get data '''
        data = {}
        for item in TobeVolunteerDB().find({'_id': uid}):
            data.update(item)
            data['uid'] = data['_id']

        return TobeVolunteerStruct.parse_obj(data).dict()

    @staticmethod
    def query(query):
        ''' query '''
        _query = {'ok': True}
        _or = []

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
