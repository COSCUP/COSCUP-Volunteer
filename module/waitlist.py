''' WaitList '''
from models.waitlistdb import WaitListDB


class WaitList:
    ''' WaitList object '''
    @staticmethod
    def join_to(pid, tid, uid, note):
        ''' Join to

        :param str pid: project id
        :param str tid: team id
        :param str uid: uid
        :param str note: note

        '''
        return WaitListDB().join_to(pid=pid, tid=tid, uid=uid, note=note)

    @staticmethod
    def is_in_wait(pid, tid, uid):
        ''' is in wait list

        :param str pid: project id
        :param str tid: team id
        :param str uid: uid

        '''
        return WaitListDB().is_in_wait(pid=pid, tid=tid, uid=uid)

    @staticmethod
    def list_by_team(pid, tid, uid=None):
        ''' List team waitting user

        :param str pid: project id
        :param str tid: team id
        :param str uid: uid

        '''
        return WaitListDB().list_by(pid=pid, tid=tid, uid=uid)

    @staticmethod
    def make_result(wid, pid, uid, result):
        ''' make result

        :param str wid: waitlist id
        :param str pid: project id
        :param str uid: user id
        :param str result: result in approval, deny.

        '''
        return WaitListDB().make_result(_id=wid, pid=pid, uid=uid, result=result)

    @staticmethod
    def find_history(uid, pid=None):
        ''' Find some one history

        :param str pid: project id
        :param str uid: user id

        '''
        query = {'uid': uid}
        if pid is not None:
            query['pid'] = pid

        return WaitListDB().find(query)

    @staticmethod
    def find_history_in_team(uid, pid, tid):
        ''' Find some one history in team

        :param str uid: user id
        :param str pid: project id
        :param str tid: team id

        '''
        for raw in WaitListDB().find({'pid': pid, 'tid': tid, 'uid': uid}):
            yield raw
