''' ExpenseDB '''
import string
from datetime import datetime
from random import choices
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class ExpenseDB(DBBase):
    ''' Expense Collection '''

    def __init__(self):
        super().__init__('expense')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ('tid', 1)])
        self.create_index([('pid', 1), ('tid', 1), ('request.buid', 1)])
        self.create_index([('pid', 1), ('tid', 1), ('create_by', 1)])

    @staticmethod
    def status():
        ''' Status mapping '''
        return {'1': '已申請',
                '2': '已出款',
                '3': '已完成',
                }

    @staticmethod
    def new(pid, tid, uid):
        ''' Create new '''
        return {
            '_id': f'{uuid4().node:x}',
            'pid': pid,
            'tid': tid,
            'request': {},
            'invoices': [],
            'bank': {},
            'status': '1',  # 已申請/已出款/已完成
            'note': {'myself': '', 'to_create': ''},
            'code': f"E-{''.join(choices(string.ascii_uppercase+string.digits, k=4))}",
            'relevant_code': [],
            'create_by': uid,
            'create_at': datetime.today(),
        }

    def add(self, data):
        ''' Add data

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'pid': data['pid'], 'tid': data['tid'], '_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
