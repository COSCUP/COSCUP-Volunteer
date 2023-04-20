''' Team '''
from typing import Any, Generator, Optional
from uuid import uuid4

from pymongo.cursor import Cursor

from models.teamdb import TeamDB, TeamMemberChangedDB, TeamMemberTagsDB
from structs.teams import TeamBase, TeamUsers


class Team:
    ''' Team module '''

    @staticmethod
    def create(pid: str, tid: str, name: str, owners: list[str]) -> TeamBase:
        ''' Create team

        :param str pid: project id
        :param str tid: team id
        :param str name: team name
        :param list owners: owners

        '''
        if not tid or not pid or not owners:
            raise Exception('lost required')

        teamdb = TeamDB(pid, tid)
        data = TeamBase.parse_obj(
            {'pid': pid, 'tid': tid, 'name': name, 'owners': owners})
        return teamdb.add(data)

    @staticmethod
    def update_chiefs(pid: str, tid: str,
                      add_uids: Optional[list[str]] = None,
                      del_uids: Optional[list[str]] = None) -> None:
        ''' update chiefs

        :param list add_uids: add uids
        :param list del_uids: del uids

        '''
        teamdb = TeamDB(pid, tid)
        teamdb.update_users(
            field='chiefs', add_uids=add_uids, del_uids=del_uids)

    @staticmethod
    def update_members(pid: str, tid: str,
                       add_uids: Optional[list[str]] = None,
                       del_uids: Optional[list[str]] = None,
                       make_record: bool = True) -> None:
        ''' update chiefs

        :param list add_uids: add uids
        :param list del_uids: del uids
        :param bool make_record: make user update record

        .. note:: also make user changed record

        '''
        teamdb = TeamDB(pid, tid)
        teamdb.update_users(
            field='members', add_uids=add_uids, del_uids=del_uids)

        if make_record:
            TeamMemberChangedDB().make_record(
                pid=pid, tid=tid, action={'add': add_uids, 'del': del_uids})

    @staticmethod
    def list_by_pid(pid: str, show_all: bool = False) -> Generator[TeamBase, None, None]:
        ''' List all team in project

        :param str pid: project id

        '''
        if show_all:
            for team in TeamDB('', '').find({'pid': pid}):
                yield TeamBase.parse_obj(team)

        else:
            for team in TeamDB('', '').find({
                'pid': pid,
                    '$or': [{'disabled': {'$exists': False}}, {'disabled': False}]}):
                yield TeamBase.parse_obj(team)

    @staticmethod
    def get(pid: str, tid: str) -> TeamBase | None:
        ''' Get team data

        :param str pid: project id
        :param str tid: team id

        '''
        return TeamDB(pid=pid, tid=tid).get()

    @staticmethod
    def participate_in(uid: str, pid: Optional[list[str]] = None) -> Cursor[dict[str, Any]]:
        ''' participate in

        :param str uid: uid

        '''
        query: dict[str, Any] = {
            '$or': [
                {'members': uid, '$or': [
                    {'disabled': {'$exists': False}}, {'disabled': False}]},
                {'chiefs': uid, '$or': [
                    {'disabled': {'$exists': False}}, {'disabled': False}]},
            ],
        }

        if pid:
            query['pid'] = {'$in': pid}

        return TeamDB('', '').find(query)

    @staticmethod
    def update_setting(pid: str, tid: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        ''' update setting

        :param str pid: project id
        :param str tid: team id
        :param dict data: data

        '''
        teamdb = TeamDB(pid=pid, tid=tid)
        _data = {}
        for k in ('name', 'public_desc', 'desc', 'chiefs', 'members',
                  'owners', 'headcount', 'mailling', 'disabled'):
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

        return None

    @staticmethod
    def get_users(pid: str, tids: list[str]) -> dict[str, Any]:
        ''' Get all users by team

        :param str pid: project id
        :param list tid: team id

        '''
        users = {}
        for tid in tids:
            team = TeamDB(pid=pid, tid=tid).get()
            if not team:
                raise Exception(f"no team: {tid}")

            teamusers = TeamUsers.parse_obj(team)
            users[tid] = teamusers.chiefs + teamusers.members

        return users

    @staticmethod
    def add_tag_member(pid: str, tid: str,
                       tag_name: str, tag_id: Optional[str] = None) -> dict[str, Any]:
        ''' Add tag member

        :param str pid: project id
        :param str tid: team id
        :param str tag_id: tag id
        :param str tag_name: tag name

        '''
        if tag_id is None:
            tag_id = f'{uuid4().fields[0]:08x}'

        data = {'id': tag_id, 'name': tag_name.strip()}
        TeamDB(pid=pid, tid=tid).add_tag_member(tag_data=data)

        return data

    @staticmethod
    def add_tags_to_members(pid: str, tid: str, data: dict[str, Any]) -> None:
        ''' Add tags to member

        :param str pid: project id
        :param str tid: team id
        :param dict data: {uid: [tag_id, ...]}

        '''
        team_member_tags_db = TeamMemberTagsDB()
        for uid in data:
            team_member_tags_db.update_and_add(
                pid=pid, tid=tid, uid=uid, tags=data[uid])

    @staticmethod
    def del_tag(pid: str, tid: str, tag_id: str) -> None:
        ''' Delete tag '''
        TeamDB(pid=pid, tid=tid).update_one(
            {'pid': pid, 'tid': tid},
            {'$pull': {'tag_members': {'id': tag_id}}}
        )
        TeamMemberTagsDB().update_many(
            {'pid': pid, 'tid': tid},
            {'$pull': {'tags.tags': tag_id}}
        )

    @staticmethod
    def get_members_tags(pid: str, tid: str) -> dict[str, Any]:
        ''' Get members tags info '''
        datas = {}
        for raw in TeamMemberTagsDB().find({'pid': pid, 'tid': tid}):
            datas[raw['uid']] = raw['tags']

        return datas

    @staticmethod
    def get_members_uid_by_tags(pid: str, tid: str, tags: list[str]) -> list[str]:
        ''' Get members by tags '''
        _or = []
        for tag in tags:
            _or.append({'tags.tags': tag})

        query: dict[str, Any] = {'pid': pid, 'tid': tid}
        query['$or'] = _or

        uids = []
        for raw in TeamMemberTagsDB().find(query):
            uids.append(raw['uid'])

        return uids

    @staticmethod
    def get_tags_by_uids(pid: str, tid: str, uids: list[str]) -> dict[str, Any]:
        ''' Get tags by uids '''
        datas = {}
        for raw in TeamMemberTagsDB().find({'pid': pid, 'tid': tid, 'uid': {'$in': uids}}):
            datas[raw['uid']] = raw['tags']['tags']

        for uid in uids:
            if uid not in datas:
                datas[uid] = []

        return datas
