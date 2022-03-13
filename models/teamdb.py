from time import time
from typing import TypedDict

from pymongo.collection import ReturnDocument

from models.base import DBBase


class AddTagMemberPayload(TypedDict):
    id: str
    name: str


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

    def __init__(self, pid: str, tid: str):
        super(TeamDB, self).__init__('team')
        self.pid = pid
        self.tid = tid

    def index(self):
        self.create_index([
            ('chiefs', 1),
        ])
        self.create_index([
            ('members', 1),
        ])
        self.create_index([
            ('pid', 1),
        ])

    def default(self):
        r = {
            'pid': self.pid,
            'tid': self.tid,
            'name': '',
            'owners': [],
            'chiefs': [],
            'members': [],
            'desc': '',
            'tag_members': [],
        }
        self.make_create_at(r)
        return r

    def add(self, data: dict):
        return self.find_one_and_update(
            {
                'pid': self.pid,
                'tid': self.tid
            },
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def update_setting(self, data: dict):
        return self.find_one_and_update(
            {
                'pid': self.pid,
                'tid': self.tid
            },
            {'$set': data},
            return_document=ReturnDocument.AFTER,
        )

    def update_users(self, field: str, add_uids: list, del_uids: list):
        if add_uids:
            self.find_one_and_update({
                'pid': self.pid,
                'tid': self.tid
            }, {'$addToSet': {
                field: {
                    '$each': add_uids
                }
            }})

        if del_uids:
            self.find_one_and_update({
                'pid': self.pid,
                'tid': self.tid
            }, {'$pullAll': {
                field: del_uids
            }})

    def get(self):
        ''' Get data '''
        return self.find_one({'pid': self.pid, 'tid': self.tid})

    def add_tag_member(self, tag_data: AddTagMemberPayload):
        ''' Add tag member '''
        for data in self.find({
                'pid': self.pid,
                'tid': self.tid
        }, {'tag_members': 1}):
            if 'tag_members' not in data:
                data['tag_members'] = []

            tags = {}
            for tag in data['tag_members']:
                tags[tag['id']] = tag

            tags[tag_data['id']] = tag_data

            self.find_one_and_update(
                {
                    'pid': self.pid,
                    'tid': self.tid
                },
                {'$set': {
                    'tag_members': list(tags.values())
                }},
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
        super(TeamMemberTagsDB, self).__init__('team_member_tags')

    def index(self):
        self.create_index([('pid', 1), ('tid', 1)])

    def update(self, pid: str, tid: str, uid: str, tags: list):
        ''' update team '''
        return self.find_one_and_update(
            {
                'pid': pid,
                'tid': tid,
                'uid': uid
            },
            {'$set': {
                'tags': tags
            }},
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
        super(TeamMemberChangedDB, self).__init__('team_member_changed')

    def index(self):
        ''' Index '''
        self.create_index([
            ('pid', 1),
        ])
        self.create_index([
            ('case', 1),
        ])

    def make_record(self,
                    pid: str,
                    tid: str,
                    add_uids: list | None = None,
                    del_uids: list | None = None,
                    waiting_uids: list | None = None,
                    deny_uids: list | None = None):
        ''' make record

        .. note::
            - waiting: user send request, and waiting.
            - deny: user send request, but deny.
            - add/approve: join.
            - del: was joined, but remove.

        '''
        if add_uids:
            query = [{
                'pid': pid,
                'tid': tid,
                'case': 'add',
                'uid': uid,
                'create_at': time()
            } for uid in add_uids if uid]
            if query:
                self.insert_many(query)

        if del_uids:
            query = [{
                'pid': pid,
                'tid': tid,
                'case': 'del',
                'uid': uid,
                'create_at': time()
            } for uid in del_uids if uid]
            if query:
                self.insert_many(query)

        if waiting_uids:
            query = [{
                'pid': pid,
                'tid': tid,
                'case': 'waiting',
                'uid': uid,
                'create_at': time()
            } for uid in waiting_uids if uid]
            if query:
                self.insert_many(query)

        if deny_uids:
            query = [{
                'pid': pid,
                'tid': tid,
                'case': 'deny',
                'uid': uid,
                'create_at': time()
            } for uid in deny_uids if uid]
            if query:
                self.insert_many(query)


class TeamPlanDB(DBBase):
    ''' TeamPlan Collection '''

    def __init__(self):
        super(TeamPlanDB, self).__init__('team_plan')

    def index(self):
        self.create_index([
            ('pid', 1),
        ])

    def save(self, pid: str, tid: str, data: list):
        return self.find_one_and_update(
            {
                'pid': pid,
                'tid': tid
            },
            {'$set': {
                'data': data
            }},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
