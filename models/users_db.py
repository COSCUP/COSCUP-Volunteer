''' User database '''
from time import time
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class UsersDB(DBBase):
    ''' UsersDB Collection '''

    def __init__(self):
        super().__init__('users')

    def index(self):
        ''' Index '''
        self.create_index([('mail', 1), ])
        self.create_index([('property.suspend', 1), ])

    @staticmethod
    def new(mail):
        ''' New user account

        :param str mail: mail
        :rtype: dict

        .. note:: ``mail`` bind to login oauth account. Maybe need ``alias`` for
        some case.

        '''
        return {
            '_id': f'{uuid4().fields[0]:08x}',
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


class TobeVolunteerDB(DBBase):
    ''' TobeVolunteer Collection '''

    def __init__(self):
        super().__init__('tobe_volunteer')

    def add(self, data: dict):
        ''' add '''
        self.find_one_and_update(
            {'_id': data['uid']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
