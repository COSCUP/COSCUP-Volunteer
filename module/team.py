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
