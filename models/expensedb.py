from datetime import datetime
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class ExpenseDB(DBBase):
    ''' Expense Collection '''

    def __init__(self):
        super(ExpenseDB, self).__init__('expense')

    def index(self):
        self.create_index([('pid', 1), ('tid', 1)])
        self.create_index([('pid', 1), ('tid', 1), ('request.buid', 1)])
        self.create_index([('pid', 1), ('tid', 1), ('create_by', 1)])

    @staticmethod
    def status():
        return {
            '1': u'已申請',
            '2': u'已出款',
            '3': u'已完成',
        }

    @staticmethod
    def new(pid, tid, uid):
        return {
            '_id': u'%x' % uuid4().node,
            'pid': pid,
            'tid': tid,
            'request': {},
            'invoices': [],
            'bank': {},
            'status': '1',  # 已申請/已出款/已完成
            'note': {
                'myself': '',
                'to_create': ''
            },
            'create_by': uid,
            'create_at': datetime.today(),
        }

    def add(self, data: dict):
        return self.find_one_and_update(
            {
                'pid': data['pid'],
                'tid': data['tid'],
                '_id': data['_id']
            },
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
