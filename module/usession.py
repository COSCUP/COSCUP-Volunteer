''' USession '''
from time import time
from typing import Any, Generator, Optional

from pymongo.results import InsertOneResult, UpdateResult

from models.usessiondb import USessionDB
from module.mc import MC


class USession:
    ''' USession Class '''
    @staticmethod
    def make_new(uid: str, header: dict[str, Any]) -> InsertOneResult:
        ''' make new session record

        :param str uid: uid
        :param dict header: headers

        '''
        doc = {'uid': uid, 'header': header,
               'created_at': time(), 'alive': True}
        return USessionDB().add(doc)

    @staticmethod
    def get(sid: Optional[str]) -> Optional[dict[str, Any]]:
        ''' Get usession data

        :param str sid: usession id

        '''
        return USessionDB(token=sid).get()

    @staticmethod
    def get_no_ipinfo() -> Generator[dict[str, Any], None, None]:
        ''' Get no ipinfo '''
        for raw in USessionDB().find({'ipinfo': {'$exists': False}},
                                     {'header.X-Real-Ip': 1, 'header.X-Forwarded-For': 1}):
            yield raw

    @staticmethod
    def update_ipinfo(sid: str, data: dict[str, Any]) -> None:
        ''' Update session ipinfo

        :param str sid: usession id

        '''
        USessionDB().find_one_and_update(
            {'_id': sid}, {'$set': {'ipinfo': data}})

    @staticmethod
    def get_recently(uid: str, limit: int = 25) -> Generator[dict[str, Any], None, None]:
        ''' Get recently record

        :param str uid: uid

        '''
        for raw in USessionDB(token='').find({'uid': uid},
                                             sort=(('created_at', -1), ),
                                             limit=limit):
            yield raw

    @staticmethod
    def get_alive(uid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get alive session

        :param str uid: uid

        '''
        for raw in USessionDB(token='').find({'uid': uid, 'alive': True},
                                             sort=(('created_at', -1), )):
            yield raw

    @staticmethod
    def make_dead(sid: str, uid: Optional[str] = None) -> None:
        ''' Make session to dead

        :param str sid: sid
        :param str uid: uid

        '''
        query = {'_id': sid}
        if uid:
            query['uid'] = uid

        USessionDB(token='').find_one_and_update(
            query, {'$set': {'alive': False}})
        MC.get_client().delete(f'sid:{sid}')

    @staticmethod
    def clean(days: int = 3) -> UpdateResult:
        ''' Make expired

        :param int days: days

        '''
        target = time() - 86400*days
        return USessionDB(token='').update_many(
            {'alive': True, 'created_at': {'$lte': target}},
            {'$set': {'alive': False}},
        )
