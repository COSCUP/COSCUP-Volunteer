from time import time
from uuid import uuid4

from pymongo.collection import ReturnDocument

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

        .. note:: ``mail`` bind to login oauth account. Maybe need ``alias`` for
        some case.

        '''
        return {
            '_id': '%x' % uuid4().fields[0],
            'mail': mail,
            'created_at': int(time()),
        }

    def add(self, data):
        ''' Add data

        :param dict data: user data
        :rtype: dict

        '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
