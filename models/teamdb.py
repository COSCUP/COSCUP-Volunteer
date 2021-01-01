from time import time

from pymongo.collection import ReturnDocument

from models.base import DBBase


class TeamDB(DBBase):
    ''' Team Collection

    :Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``name``: team name
        - ``owners``: (list) owners for team admin
        - ``chiefs``: (list) team chiefs
        - ``members``: (list) team members

    '''
    def __init__(self, pid, tid):
        super(TeamDB, self).__init__('team')
        self.pid = pid
        self.tid = tid

    def index(self):
        ''' Index '''
        self.create_index([('chiefs', 1), ])
        self.create_index([('members', 1), ])
        self.create_index([('pid', 1), ])

    def default(self):
        ''' default data '''
        r = {
            'pid': self.pid,
            'tid': self.tid,
            'name': '',
            'owners': [],
            'chiefs': [],
            'members': [],
            'desc': '',
        }
        self.make_create_at(r)
        return r

    def add(self, data):
        ''' Add data

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'pid': self.pid, 'tid': self.tid},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def update_setting(self, data):
        ''' update setting

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'pid': self.pid, 'tid': self.tid},
            {'$set': data},
            return_document=ReturnDocument.AFTER,
        )


    def update_users(self, field, add_uids, del_uids):
        ''' Update users

        :param str field: field name
        :param list add_uids: add uids
        :param list del_uids: del uids

        '''
        if add_uids:
            self.find_one_and_update(
                {'pid': self.pid, 'tid': self.tid},
                {'$addToSet': {field: {'$each': add_uids}}})

        if del_uids:
            self.find_one_and_update(
                {'pid': self.pid, 'tid': self.tid},
                {'$pullAll': {field: del_uids}})

    def get(self):
        ''' Get data '''
        return self.find_one({'pid': self.pid, 'tid': self.tid})


class TeamMemberChangedDB(DBBase):
    ''' TeamMemberChangedDB Collection

    :Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``uid``: user id
        - ``case``: ``add``, ``del``, ``waiting``

    '''
    def __init__(self):
        super(TeamMemberChangedDB, self).__init__('team_member_changed')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ])
        self.create_index([('case', 1), ])

    def make_record(self, pid, tid, add_uids=None, del_uids=None, waiting_uids=None, deny_uids=None):
        ''' make record

        :param str pid: project id
        :param str tid: team id
        :param list add_uids: add user list
        :param list del_uids: del user list
        :param list waiting_uids: waiting user list

        .. note::
            - waiting: user send request, and waiting.
            - deny: user send request, but deny.
            - add/approve: join.
            - del: was joined, but remove.

        '''
        if add_uids:
            query = [{'pid': pid, 'tid': tid, 'case': 'add', 'uid': uid, 'create_at': time()} for uid in add_uids if uid]
            if query:
                self.insert_many(query)

        if del_uids:
            query = [{'pid': pid, 'tid': tid, 'case': 'del', 'uid': uid, 'create_at': time()} for uid in del_uids if uid]
            if query:
                self.insert_many(query)

        if waiting_uids:
            query = [{'pid': pid, 'tid': tid, 'case': 'waiting', 'uid': uid, 'create_at': time()} for uid in waiting_uids if uid]
            if query:
                self.insert_many(query)

        if deny_uids:
            query = [{'pid': pid, 'tid': tid, 'case': 'deny', 'uid': uid, 'create_at': time()} for uid in deny_uids if uid]
            if query:
                self.insert_many(query)


class TeamPlanDB(DBBase):
    ''' TeamPlan Collection '''
    def __init__(self):
        super(TeamPlanDB, self).__init__('team_plan')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ])

    def save(self, pid, tid, data):
        ''' Save data

        :param str pid: project id
        :param str tid: team id
        :patam list data: plan data

        '''
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid},
            {'$set': {'data': data}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
