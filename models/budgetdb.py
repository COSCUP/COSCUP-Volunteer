from datetime import datetime
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase

class BudgetDB(DBBase):
    ''' Budget Collection

    :Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``bid``: budget id
        - ``name``: team name
        - ``uid``: user id
        - ``currency``: TWD, USD
        - ``total``: 0.00
        - ``paydate``: ISO8601
        - ``desc``: desc
        - ``estimate``: estimate
        - ``create_at``: create date

    '''
    def __init__(self):
        super(BudgetDB, self).__init__('budget')

    def index(self):
        self.create_index([('pid', 1), ('tid', 1)])
        self.create_index([('pid', 1), ('bid', 1)])

    @staticmethod
    def new(pid, tid, uid):
        return {
            '_id': u'%x' % uuid4().node,
            'pid': pid,
            'tid': tid,
            'bid': '',
            'name': '',
            'uid': uid,
            'currency': 'TWD',
            'total': 0,
            'paydate': '',
            'desc': '',
            'estimate': '',
            'enabled': True,
            'create_at': datetime.today(),
        }

    def add(self, data: dict):
        return self.find_one_and_update(
            {'pid': data['pid'], 'tid': data['tid'], '_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def edit(self, _id, data: dict):
        return self.find_one_and_update(
            {'_id': _id},
            {'$set': data},
            return_document=ReturnDocument.AFTER,
        )

