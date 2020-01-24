from models.waitlistdb import WaitListDB


class WaitList(object):
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
