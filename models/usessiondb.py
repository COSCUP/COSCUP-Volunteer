import hashlib
from time import time
from uuid import uuid4

from models.base import DBBase


class USessionDB(DBBase):
    ''' USessionDB Collection '''
    def __init__(self, token=None):
        super(USessionDB, self).__init__('usession')

        if token is None:
            m = hashlib.sha256()
            m.update(('%s%s' % (uuid4().hex, time())).encode('utf8'))
            token = m.hexdigest()

        self.token = token

    def save(self, data):
        ''' save

        :param dict data: data

        '''
        doc = {}
        doc.update(data)
        doc['_id'] = self.token

        return self.insert_one(doc)

    def get(self):
        ''' Get data '''
        return self.find_one({'_id': self.token})
