''' WaitList '''
from typing import Any, Generator, Literal, Optional

from pymongo.cursor import Cursor

from models.waitlistdb import WaitListDB


class WaitList:
    ''' WaitList object '''
    @staticmethod
    def join_to(pid: str, tid: str, uid: str, note: str) -> dict[str, Any]:
        ''' Join to

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.
            note (str): Note.

        Returns:
            Return the datas.

        '''
        return WaitListDB().join_to(pid=pid, tid=tid, uid=uid, note=note)

    @staticmethod
    def is_in_wait(pid: str, tid: str, uid: str) -> int:
        ''' is in wait list

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.

        Returns:
            Return the numbers.

        '''
        return WaitListDB().is_in_wait(pid=pid, tid=tid, uid=uid)

    @staticmethod
    def list_by_team(pid: str, tid: str, uid: Optional[str] = None) -> \
            Generator[dict[str, Any], None, None] | None:
        ''' List team waiting user

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.

        Returns:
            Return the datas.

        '''
        return WaitListDB().list_by(pid=pid, tid=tid, uid=uid)

    @staticmethod
    def make_result(wid: str, pid: str, uid: str,
                    result: Literal['approval', 'deny']) -> Optional[dict[str, Any]]:
        ''' make result

        Args:
            wid (str): Waitlist id.
            pid (str): Project id.
            uid (str): User id.
            result (str): List in `approval`, `deny`.

        Returns:
            Return the data.

        '''
        return WaitListDB().make_result(_id=wid, pid=pid, uid=uid, result=result)

    @staticmethod
    def find_history(uid: str, pid: Optional[str] = None) -> Cursor[dict[str, Any]]:
        ''' Find some one history

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            Return the [pymongo.cursor.Cursor][] object.

        '''
        query = {'uid': uid}
        if pid is not None:
            query['pid'] = pid

        return WaitListDB().find(query)

    @staticmethod
    def find_history_in_team(uid: str, pid: str, tid: str) -> Generator[dict[str, Any], None, None]:
        ''' Find some one history in team

        Args:
            uid (str): User id.
            pid (str): Project id.
            tid (str): Team id.

        Yields:
            Return the datas.

        '''
        for raw in WaitListDB().find({'pid': pid, 'tid': tid, 'uid': uid}):
            yield raw

    @staticmethod
    def get_note(pid: str, tid: str, uid: str) -> Generator[dict[str, str], None, None]:
        ''' Get note

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.

        Yields:
            Return the datas.

        '''
        for raw in WaitListDB().find(
            filter={'pid': pid, 'tid': tid, 'uid': uid},
            projection={'_id': 0},
            sort=(('_id', -1), ),
            limit=1,
        ):
            yield raw
