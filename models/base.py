import setting

import pymongo
from pymongo.collection import Collection


class DBBase(Collection):
    ''' DBBase class

    :param str name: collection name

    '''
    def __init__(self, name):
        client = pymongo.MongoClient('mongodb://%s:%s' % (
                setting.MONGO_HOST, setting.MONGO_PORT))[setting.MONGO_DBNAME]

        super(DBBase, self).__init__(client, name)


class TestDB(DBBase):
    def __init__(self):
        super(TestDB, self).__init__('test_')


if __name__ == '__main__':
    test = TestDB()
    pid = test.insert_one({'name': 'Toomore', 'age': 35}).inserted_id
    print(pid)
