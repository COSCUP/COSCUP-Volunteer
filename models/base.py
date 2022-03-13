from time import time

import pymongo
from pymongo.collection import Collection

import setting


class DBBase(Collection):
    def __init__(self, name: str):
        client = pymongo.MongoClient('mongodb://%s:%s' % (
                setting.MONGO_HOST, setting.MONGO_PORT))[setting.MONGO_DBNAME]

        super(DBBase, self).__init__(client, name)

    @staticmethod
    def make_create_at(data: dict):
        ''' make create_at timestamp'''
        data['created_at'] = time()


class TestDB(DBBase):
    def __init__(self):
        super(TestDB, self).__init__('test_')


if __name__ == '__main__':
    test = TestDB()
    pid = test.insert_one({'name': 'Toomore', 'age': 35}).inserted_id
    print(pid)
