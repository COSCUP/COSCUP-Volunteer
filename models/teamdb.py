''' TeamDB '''
from time import time
from typing import Any, Optional

from pymongo.collection import ReturnDocument

from models.base import DBBase
from structs.teams import TeamBase


class TeamDB(DBBase):
    ''' Team Collection

    Args:
        pid (str): Project id.
        tid (str): Team id.

    Attributes:
        pid (str): Project id.
        tid (str): Team id.

    Note:
        For some use cases, the `pid`, `tid` could be empty strings.

    '''

    def __init__(self, pid: str | None, tid: str | None) -> None:
        super().__init__('team')
        self.pid = pid
        self.tid = tid

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `chiefs`
            - `members`
            - `pid`

        '''
        self.create_index([('chiefs', 1), ])
        self.create_index([('members', 1), ])
        self.create_index([('pid', 1), ])

    def default(self) -> dict[str, Any]:
        ''' default data

        Returns:
            Return a default struct.

        Struct:
            - ``pid``: Project id.
            - ``tid``: Team id.
            - ``name``: Team name.
            - ``owners``: `list` List of `uid` as team admin.
            - ``chiefs``: `list` List of `uid` as team chiefs.
            - ``members``: `list` List of `uid` as team members.
            - ``desc``: Description.
            - ``tag_members``: List of data
                               `{'id': '<random code>', 'name': '<tag name>'}`.
                               The tags for team to mark on members.

        TODO:
            Need refactor in pydantic.

        '''
        result: dict[str, str | list[str] | None] = {
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

    def add(self, data: TeamBase) -> TeamBase:
        ''' Add data

        Args:
            data (TeamBase): The data to inserted / updated.

        Returns:
            Return the inserted / updated data.

        '''
        return TeamBase.parse_obj(self.find_one_and_update(
            {'pid': self.pid, 'tid': self.tid},
            {'$set': data.dict(exclude_none=True)},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        ))

    def update_setting(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' update setting

        Args:
            data (dict): The data to inserted / updated.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'pid': self.pid, 'tid': self.tid},
            {'$set': data},
            return_document=ReturnDocument.AFTER,
        )

    def update_users(self, field: str,
                     add_uids: Optional[list[str]] = None,
                     del_uids: Optional[list[str]] = None) -> None:
        ''' Update users

        Args:
            field (str): The `field` should be `chiefs`, `members`, `owners`.
            add_uids (list): Optional, list of uids for add them into the `field`.
            del_uids (list): Optional, list of uids for delete them from the `field`.

        '''
        if add_uids:
            self.find_one_and_update(
                {'pid': self.pid, 'tid': self.tid},
                {'$addToSet': {field: {'$each': add_uids}}})

        if del_uids:
            self.find_one_and_update(
                {'pid': self.pid, 'tid': self.tid},
                {'$pullAll': {field: del_uids}})

    def get(self) -> TeamBase | None:
        ''' Get data

        Returns:
            Return the team info in `pid`, `tid`.

        '''
        for team in self.find({'pid': self.pid, 'tid': self.tid}):
            return TeamBase.parse_obj(team)

        return None

    def add_tag_member(self, tag_data: dict[str, str]) -> None:
        ''' Add tag member

        Args:
            tag_data (dict): The tag data should be:

                `{'id': '<random code>', 'name': '<tag name>'}`.

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

    Save the member's tag info.

    Struct:
        - ``pid``: Project id.
        - ``tid``: Team id.
        - ``uid``: User id.
        - ``tags``: List of tag id.

    TODO:
        Need refactor in pydantic.

    '''

    def __init__(self) -> None:
        super().__init__('team_member_tags')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`, `tid`

        '''
        self.create_index([('pid', 1), ('tid', 1)])

    def update_and_add(self, pid: str, tid: str, uid: str, tags: list[str]) -> dict[str, Any]:
        ''' update team

        Args:
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.
            tags (list): List of tag id.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid, 'uid': uid},
            {'$set': {'tags': tags}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


class TeamMemberChangedDB(DBBase):
    ''' TeamMemberChangedDB Collection

    Struct:
        - ``pid``: from project id
        - ``tid``: team id
        - ``uid``: user id
        - ``case``: ``add``, ``del``, ``waiting``

    TODO:
        Need refactor in pydantic.

    '''

    def __init__(self) -> None:
        super().__init__('team_member_changed')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`
            - `case`

        '''
        self.create_index([('pid', 1), ])
        self.create_index([('case', 1), ])

    def make_record(self, pid: str, tid: str, action: dict[str, Optional[list[str]]]) -> None:
        ''' make record

        Args:
            pid (str): Project id.
            tid (str): Team id.
            action (dict):

                - `add`: Optional, list of uids. Add or approve to join.
                - `del`: Optional, list of uids. Was joined, but remove now.
                - `waiting`: Optional, list of uids. User has sent the request,
                             and waiting the chiefs to review.
                - `deny`: Optional, list of uids. User has sent the request,
                          but has to deny.

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

    def __init__(self) -> None:
        super().__init__('team_plan')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`

        '''
        self.create_index([('pid', 1), ])

    def add(self, pid: str, tid: str, data: list[dict[str, Any]]) -> dict[str, Any]:
        ''' Save data

        Args:
            pid (str): Project id.
            tid (str): Team id.
            data (dict): List of data to inserted / updated.

                - `title`: Plan title.
                - `start`: Date in `YYYY-MM-DD` format.
                - `end`: Date in `YYYY-MM-DD` format.
                - `desc`: Description.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'pid': pid, 'tid': tid},
            {'$set': {'data': data}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
