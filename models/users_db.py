from uuid import uuid4
from models.base import DBBase

class UsersDB(DBBase):
    ''' UsersDB Collection '''
    def __init__(self):
        super(UsersDB, self).__init__('users')

    @staticmethod
    def new(mail):
        ''' New user account

        :param str mail: mail
        :rtype: dict

        '''
        return {
            '_id': '%x' % uuid4().fields[0],
            'mail': mail,
        }

    def add(self, data):
        ''' Add data

        :param dict data: user data

        '''
        self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
        )
