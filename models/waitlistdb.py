''' WaitListDB '''
from typing import Any, Literal, Optional, Union

from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from pymongo.cursor import Cursor

from models.base import DBBase


class WaitListDB(DBBase):
    ''' WaitList Collection '''

    def __init__(self) -> None:
        super().__init__('waitlist')

    def index(self) -> None:
        ''' Index '''
        self.create_index([('pid', 1), ])
        self.create_index([('uid', 1), ])

    def join_to(self, pid: str, tid: str, uid: str, note: Optional[str] = None) -> dict[str, Any]:
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

    def is_in_wait(self, pid: str, tid: str, uid: str) -> int:
        ''' Is in waitting list

        :param str pid: project id
        :param str tid: team id
        :param str uid: user id

        '''
        return self.count_documents({
            'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}})

    def list_by(self, pid: str, tid: Optional[str] = None, uid: Optional[str] = None,
                _all: bool = False) -> Union[Optional[dict[str, Any]], Cursor[dict[str, Any]]]:
        ''' List by

        :param str pid: project id
        :param str tid: team id
        :param str uid: user id
        :param bool _all: show all waitlist

        '''
        query: dict[str, Any] = {'pid': pid}
        if tid:
            query['tid'] = tid

        if uid:
            query['uid'] = uid

        if not _all:
            query['result'] = {'$exists': False}

        if 'uid' in query:
            return self.find_one(query)

        return self.find(query)

    def make_result(self, _id: str, pid: str, uid: str,
                    result: Literal['approval', 'deny']) -> Optional[dict[str, Any]]:
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
