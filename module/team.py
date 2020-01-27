from models.teamdb import TeamDB


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

    def update_members(pid, tid, add_uids=None, del_uids=None):
        ''' update chiefs

        :param list add_uids: add uids
        :param list del_uids: del uids

        '''
        teamdb = TeamDB(pid, tid)
        teamdb.update_users(field='members', add_uids=add_uids, del_uids=del_uids)

    @staticmethod
    def list_by_pid(pid):
        ''' List all team in project

        :param str pid: project id

        '''
        return TeamDB(None, None).find({'pid': pid})

    @staticmethod
    def get(pid, tid):
        ''' Get team data

        :param str pid: project id
        :param str tid: team id

        '''
        return TeamDB(pid=pid, tid=tid).get()

    @staticmethod
    def participate_in(uid):
        ''' participate in

        :param str uid: uid

        '''
        return TeamDB(None, None).find({'$or': [{'members': uid}, {'chiefs': uid}]})

    @staticmethod
    def update_setting(pid, tid, data):
        ''' update setting

        :param str pid: project id
        :param str tid: team id
        :param dict data: data

        '''
        teamdb = TeamDB(pid=pid, tid=tid)
        _data = {}
        for k in ('name', 'public_desc', 'desc', 'chiefs', 'members', 'owners'):
            if k in data:
                _data[k] = data[k]

        for k in ('chiefs', 'members', 'owners'):
            if k in _data:
                if not _data[k]:
                    _data[k] = []
                    continue
                if isinstance(_data[k], str):
                    _data[k] = _data[k].split(',')

        if _data:
            return teamdb.update_setting(_data)
