''' TeamDB '''
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
        super().__init__('team')
        self.pid = pid
        self.tid = tid

    def index(self):
        ''' Index '''
        self.create_index([('chiefs', 1), ])
        self.create_index([('members', 1), ])
        self.create_index([('pid', 1), ])

    def default(self):
        ''' default data '''
        result = {
            'pid': self.pid,
            'tid': self.tid,
            'name': '',
            'owners': [],
            'chiefs': [],
            'members': [],
            'desc': '',
            'tag_members': [],
        }
        self.make_create_at(result)
        return result

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

    def add_tag_member(self, tag_data):
        ''' Add tag member

        data: {'id': str, 'name': str}

        '''
        for data in self.find({'pid': self.pid, 'tid': self.tid}, {'tag_members': 1}):
            if 'tag_members' not in data:
                data['tag_members'] = []

            tags = {}
            for tag in data['tag_members']:
                tags[tag['id']] = tag

            tags[tag_data['id']] = tag_data

            self.find_one_and_update(
                {'pid': self.pid, 'tid': self.tid},
                {'$set': {'tag_members': list(tags.values())}},
            )


class TeamMemberTagsDB(DBBase):
    ''' TeamMemberTagsDB Collection

    :Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``uid``: user id
        - ``tags``: [tag_id, ...]

    '''

    def __init__(self):
        super().__init__('team_member_tags')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ('tid', 1)])

    def update_and_add(self, pid, tid, uid, tags):
        ''' update team

        :param list tags: tag_id in tags array

        '''
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid, 'uid': uid},
            {'$set': {'tags': tags}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


class TeamMemberChangedDB(DBBase):
    ''' TeamMemberChangedDB Collection

    :Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``uid``: user id
        - ``case``: ``add``, ``del``, ``waiting``

    '''

    def __init__(self):
        super().__init__('team_member_changed')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ])
        self.create_index([('case', 1), ])

    def make_record(self, pid, tid, action):
        ''' make record

        :param str pid: project id
        :param str tid: team id
        :param dict action: action in key name: add, del, waiting, deny

        .. note::
            - waiting: user send request, and waiting.
            - deny: user send request, but deny.
            - add/approve: join.
            - del: was joined, but remove.

        '''
        if 'add' in action and action['add']:
            query = [{'pid': pid, 'tid': tid, 'case': 'add', 'uid': uid,
                      'create_at': time()} for uid in action['add'] if uid]
            if query:
                self.insert_many(query)

        if 'del' in action and action['del']:
            query = [{'pid': pid, 'tid': tid, 'case': 'del', 'uid': uid,
                      'create_at': time()} for uid in action['del'] if uid]
            if query:
                self.insert_many(query)

        if 'waiting' in action and action['waiting']:
            query = [{'pid': pid, 'tid': tid, 'case': 'waiting', 'uid': uid,
                      'create_at': time()} for uid in action['waiting'] if uid]
            if query:
                self.insert_many(query)

        if 'deny' in action and action['deny']:
            query = [{'pid': pid, 'tid': tid, 'case': 'deny', 'uid': uid,
                      'create_at': time()} for uid in action['deny'] if uid]
            if query:
                self.insert_many(query)


class TeamPlanDB(DBBase):
    ''' TeamPlan Collection '''

    def __init__(self):
        super().__init__('team_plan')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ])

    def add(self, pid, tid, data):
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
