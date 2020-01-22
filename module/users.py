from models.oauth_db import OAuthDB
from models.users_db import UsersDB

from pymongo.collection import ReturnDocument


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
