from pymongo.collection import ReturnDocument

from models.base import DBBase

class WaitListDB(DBBase):
    ''' WaitList Collection '''
    def __init__(self):
        super(WaitListDB, self).__init__('waitlist')

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
            {'pid': pid, 'tid': tid, 'uid': uid},
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
        return self.count_documents({'pid': pid, 'tid': tid, 'uid': uid})
