''' WaitListDB '''
from typing import Any, Generator, Literal, Optional

from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument

from models.base import DBBase


class WaitListDB(DBBase):
    ''' WaitList Collection '''

    def __init__(self) -> None:
        super().__init__('waitlist')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`
            - `uid`

        '''
        self.create_index([('pid', 1), ])
        self.create_index([('uid', 1), ])

    def join_to(self, pid: str, tid: str, uid: str, note: Optional[str] = None) -> dict[str, Any]:
        ''' Join to

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.
            note (str): Optional. The note from user.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}},
            {'$set': {'note': note}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def is_in_wait(self, pid: str, tid: str, uid: str) -> int:
        ''' Is in waitting list

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.

        Returns:
            How many requests are in waiting.

        '''
        return self.count_documents({
            'pid': pid, 'tid': tid, 'uid': uid, 'result': {'$exists': False}})

    def list_by(self, pid: str, tid: Optional[str] = None, uid: Optional[str] = None,
                _all: bool = False) -> Generator[dict[str, Any], None, None]:
        ''' List by

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.
            _all (bool): To return all include waiting requests.

        Returns:
            If `uid` is specified, the return will be `dict` or `None`.
                Otherwise the return could be iterable.

        '''
        query: dict[str, Any] = {'pid': pid}
        if tid:
            query['tid'] = tid

        if uid:
            query['uid'] = uid

        if not _all:
            query['result'] = {'$exists': False}

        if 'uid' in query:
            data = self.find_one(query)
            if data:
                yield data
        else:
            for data in self.find(query):
                yield data

    def make_result(self, _id: str, pid: str, uid: str,
                    result: Literal['approval', 'deny']) -> Optional[dict[str, Any]]:
        ''' Make result

        Args:
            _id (str): waitlist id.
            pid (str): Project id.
            uid (str): User id.
            result (Literal): In `approval` or `deny`.

        Returns:
            Return the inserted / updated data.

        '''
        if result in ('approval', 'deny'):
            return self.find_one_and_update(
                {'_id': ObjectId(_id), 'pid': pid, 'uid': uid},
                {'$set': {'result': result}},
                return_document=ReturnDocument.AFTER,
            )

        return None
