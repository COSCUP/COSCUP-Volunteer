from models.teamdb import TeamDB
from models.teamdb import TeamMemberChangedDB


class Team(object):
    ''' Team module '''

    @staticmethod
    def create(pid, tid, name, owners):
        ''' Create team

        :param str pid: project id
        :param str tid: team id
        :param str name: team name
        :param list owners: owners

        '''
        if not tid or not pid or not owners:
            raise Exception('lost required')

        teamdb = TeamDB(pid, tid)

        data = teamdb.default()
        data['name'] = name
        data['owners'].extend(owners)

        return teamdb.add(data)

    @staticmethod
    def update_chiefs(pid, tid, add_uids=None, del_uids=None):
        ''' update chiefs

        :param list add_uids: add uids
        :param list del_uids: del uids

        '''
        teamdb = TeamDB(pid, tid)
        teamdb.update_users(field='chiefs', add_uids=add_uids, del_uids=del_uids)

    def update_members(pid, tid, add_uids=None, del_uids=None, make_record=True):
        ''' update chiefs

        :param list add_uids: add uids
        :param list del_uids: del uids
        :param bool make_record: make user update record

        .. note:: also make user changed record

        '''
        teamdb = TeamDB(pid, tid)
        teamdb.update_users(field='members', add_uids=add_uids, del_uids=del_uids)

        if make_record:
            TeamMemberChangedDB().make_record(pid=pid, tid=tid, add_uids=add_uids, del_uids=del_uids)

    @staticmethod
    def list_by_pid(pid, show_all=False):
        ''' List all team in project

        :param str pid: project id

        '''
        if show_all:
            return TeamDB(None, None).find({'pid': pid})

        return TeamDB(None, None).find({
                'pid': pid,
                '$or': [{'disabled': {'$exists': False}}, {'disabled': False}]})

    @staticmethod
    def get(pid, tid):
        ''' Get team data

        :param str pid: project id
        :param str tid: team id

        '''
        return TeamDB(pid=pid, tid=tid).get()

    @staticmethod
    def participate_in(uid, pid=None):
        ''' participate in

        :param str uid: uid

        '''
        query = {
                '$or': [
                    {'members': uid, '$or': [{'disabled': {'$exists': False}}, {'disabled': False}]},
                    {'chiefs': uid, '$or': [{'disabled': {'$exists': False}}, {'disabled': False}]},
                ],
            }

        if pid:
            query['pid'] = {'$in': pid}

        return TeamDB(None, None).find(query)

    @staticmethod
    def update_setting(pid, tid, data):
        ''' update setting

        :param str pid: project id
        :param str tid: team id
        :param dict data: data

        '''
        teamdb = TeamDB(pid=pid, tid=tid)
        _data = {}
        for k in ('name', 'public_desc', 'desc', 'chiefs', 'members', 'owners', 'headcount', 'mailling', 'disabled'):
            if k in data:
                _data[k] = data[k]

                if isinstance(_data[k], str):
                    _data[k] = _data[k].strip()

        if 'headcount' in _data:
            _data['headcount'] = int(_data['headcount'])

        for k in ('chiefs', 'members', 'owners'):
            if k in _data:
                if not _data[k]:
                    _data[k] = []
                    continue
                if isinstance(_data[k], str):
                    _data[k] = [i.strip() for i in _data[k].split(',')]

        if _data:
            return teamdb.update_setting(_data)

    @staticmethod
    def get_users(pid, tids):
        ''' Get all users by team

        :param str pid: project id
        :param list tid: team id

        '''
        users = {}
        for tid in tids:
            team = TeamDB(pid=pid, tid=tid).get()
            users[tid] = team['chiefs'] + team['members']

        return users
