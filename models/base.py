''' DB base '''
from time import time

import pymongo
from pymongo.collection import Collection

import setting


class DBBase(Collection):
    ''' DBBase class

    :param str name: collection name

    '''

    def __init__(self, name):
        client = pymongo.MongoClient(
            f'mongodb://{setting.MONGO_HOST}:{setting.MONGO_PORT}')[setting.MONGO_DBNAME]

        super().__init__(client, name)

    def __bool__(self):
        return True

    @staticmethod
    def make_create_at(data):
        ''' make create_at timestamp

        :param dict data: data

        '''
        data['created_at'] = time()
