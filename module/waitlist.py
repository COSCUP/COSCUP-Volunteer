''' WaitList '''
from typing import Any, Generator, Literal, Optional, Union

from pymongo.cursor import Cursor

from models.waitlistdb import WaitListDB


class WaitList:
    ''' WaitList object '''
    @staticmethod
    def join_to(pid: str, tid: str, uid: str, note: str) -> dict[str, Any]:
        ''' Join to

        :param str pid: project id
        :param str tid: team id
        :param str uid: uid
        :param str note: note

        '''
        return WaitListDB().join_to(pid=pid, tid=tid, uid=uid, note=note)

    @staticmethod
    def is_in_wait(pid: str, tid: str, uid: str) -> int:
        ''' is in wait list

        :param str pid: project id
        :param str tid: team id
        :param str uid: uid

        '''
        return WaitListDB().is_in_wait(pid=pid, tid=tid, uid=uid)

    @staticmethod
    def list_by_team(pid: str, tid: str, uid: Optional[str] = None) -> \
            Union[Optional[dict[str, Any]], Cursor[dict[str, Any]]]:
        ''' List team waiting user

        :param str pid: project id
        :param str tid: team id
        :param str uid: uid

        '''
        return WaitListDB().list_by(pid=pid, tid=tid, uid=uid)

    @staticmethod
    def make_result(wid: str, pid: str, uid: str,
                    result: Literal['approval', 'deny']) -> Optional[dict[str, Any]]:
        ''' make result

        :param str wid: waitlist id
        :param str pid: project id
        :param str uid: user id
        :param str result: result in approval, deny.

        '''
        return WaitListDB().make_result(_id=wid, pid=pid, uid=uid, result=result)

    @staticmethod
    def find_history(uid: str, pid: Optional[str] = None) -> Cursor[dict[str, Any]]:
        ''' Find some one history

        :param str pid: project id
        :param str uid: user id

        '''
        query = {'uid': uid}
        if pid is not None:
            query['pid'] = pid

        return WaitListDB().find(query)

    @staticmethod
    def find_history_in_team(uid: str, pid: str, tid: str) -> Generator[dict[str, Any], None, None]:
        ''' Find some one history in team

        :param str uid: user id
        :param str pid: project id
        :param str tid: team id

        '''
        for raw in WaitListDB().find({'pid': pid, 'tid': tid, 'uid': uid}):
            yield raw
