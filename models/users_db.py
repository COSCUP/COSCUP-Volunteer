from time import time
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class UsersDB(DBBase):
    ''' UsersDB Collection '''

    def __init__(self):
        super(UsersDB, self).__init__('users')

    def index(self):
        self.create_index([
            ('mail', 1),
        ])
        self.create_index([
            ('property.suspend', 1),
        ])

    @staticmethod
    def new(mail: str) -> dict:
        ''' Create a new user account

        .. note:: ``mail`` bind to login oauth account. Maybe need ``alias`` for
        some case.
        '''
        return {
            '_id': '%0.8x' % uuid4().fields[0],
            'mail': mail,
            'created_at': int(time()),
        }

    def add(self, data: dict) -> dict:
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
