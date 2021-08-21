''' DB base '''
from time import time

import setting

if setting.MONGO_MOCK:
    import mongomock
    from mongomock.collection import Collection
    from mongomock.store import DatabaseStore
    MOCK_DB_STORE = DatabaseStore()
else:
    import pymongo
    from pymongo.collection import Collection
    MOCK_DB_STORE = None


class DBBase(Collection):  # pylint: disable=abstract-method
    ''' DBBase class

    :param str name: collection name

    '''

    def __init__(self, name):
        if not setting.MONGO_MOCK:
            client = pymongo.MongoClient(
                f'mongodb://{setting.MONGO_HOST}:{setting.MONGO_PORT}')[setting.MONGO_DBNAME]
            super_args = {'database': client, 'name': name}
        else:
            client = mongomock.MongoClient()['testing']
            super_args = {'database': client, 'name': name,
                          '_db_store': MOCK_DB_STORE}

        super().__init__(**super_args)

    @staticmethod
    def make_create_at(data):
        ''' make create_at timestamp

        :param dict data: data

        '''
        data['created_at'] = time()
