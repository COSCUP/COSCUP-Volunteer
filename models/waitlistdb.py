''' WaitListDB '''
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument

from models.base import DBBase


class WaitListDB(DBBase):
    ''' WaitList Collection '''

    def __init__(self):
        super().__init__('waitlist')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ])
        self.create_index([('uid', 1), ])

    def join_to(self, pid, tid, uid, note=None):
        ''' Join to

        :param str pid: project id
        :param str tid: team id
        :param str uid: user id
        :param str note: note

        '''
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}},
            {'$set': {'note': note}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def is_in_wait(self, pid, tid, uid):
        ''' Is in waitting list

        :param str pid: project id
        :param str tid: team id
        :param str uid: user id

        '''
        return self.count_documents({
            'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}})

    def list_by(self, pid, tid=None, uid=None, _all=False):
        ''' List by

        :param str pid: project id
        :param str tid: team id
        :param str uid: user id
        :param bool _all: show all waitlist

        '''
        query = {'pid': pid}
        if tid:
            query['tid'] = tid

        if uid:
            query['uid'] = uid

        if not _all:
            query['result'] = {'$exists': False}

        if 'uid' in query:
            return self.find_one(query)

        return self.find(query)

    def make_result(self, _id, pid, uid, result):
        ''' Make result

        :param str _id: waitlist id
        :param str pid: project id
        :param str uid: user id
        :param str result: result in approval, deny.

        '''
        if result in ('approval', 'deny'):
            return self.find_one_and_update(
                {'_id': ObjectId(_id), 'pid': pid, 'uid': uid},
                {'$set': {'result': result}},
                return_document=ReturnDocument.AFTER,
            )

        return None
