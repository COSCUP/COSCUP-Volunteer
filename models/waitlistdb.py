from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument

from models.base import DBBase

class WaitListDB(DBBase):
    ''' WaitList Collection '''
    def __init__(self):
        super(WaitListDB, self).__init__('waitlist')

    def index(self):
        self.create_index([('pid', 1), ])
        self.create_index([('uid', 1), ])

    def join_to(self, pid: str, tid: str, uid: str, note: str | None = None):
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}},
            {'$set': {'note': note}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def is_in_waiting_list(self, pid: str, tid: str, uid: str):
        return self.count_documents({'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}})

    def list_by(self, pid: str, tid: str | None = None, uid: str | None = None, _all: bool = False):
        query: dict[str, dict | str] = {'pid': pid}

        if tid:
            query['tid'] = tid

        if uid:
            query['uid'] = uid

        if not _all:
            query['result'] = {'$exists': False}

        if 'uid' in query:
            return self.find_one(query)

        return self.find(query)

    def make_result(self, _id: str, pid: str, uid: str, result: str):
        if result in ('approval', 'deny'):
            return self.find_one_and_update(
                {'_id': ObjectId(_id), 'pid': pid, 'uid': uid},
                {'$set': {'result': result}},
                return_document=ReturnDocument.AFTER,
            )
