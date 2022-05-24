''' Sender DB '''
from time import time
from typing import Any
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class SenderCampaignDB(DBBase):
    ''' SenderCampaign Collection

    :Struct:
        - ``_id``: cid
        - ``name``: campaign name
        - ``created``:
            - ``pid``: pid
            - ``tid``: tid
            - ``uid``: uid
            - ``at``: created at
        - ``receiver``:
            - ``teams``: team in list
            - ``users``: user in list
            - ``team_w_tags``: team tags
            - ``all_users``: bool, send to all platform users

        - ``mail``:
            - ``subject``: subject
            - ``content``: content, support markdown

    '''

    def __init__(self) -> None:
        super().__init__('sender_campaign')

    @staticmethod
    def new(name: str, pid: str, tid: str, uid: str) -> dict[str, Any]:
        ''' new a struct '''
        return {
            '_id': uuid4().hex,
            'name': name,
            'created': {
                'pid': pid,
                'tid': tid,
                'uid': uid,
                'at': time(),
            },
            'receiver': {
                'teams': [],
                'users': [],
                'team_w_tags': {},
                'all_users': False,
            },
            'mail': {
                'subject': '',
                'content': '',
                'preheader': '',
                'layout': '1',
            },
        }

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Save data '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


class SenderLogsDB(DBBase):
    ''' SenderLogsDB Collection '''

    def __init__(self) -> None:
        super().__init__('sender_logs')

    def add(self, cid: str, layout: str, desc: str, receivers: list[dict[str, Any]]) -> None:
        ''' Save log

        :param str cid: cid
        :param str layout: layout
        :param str desc: desc
        :param list receivers: receivers

        '''

        data = {
            'cid': cid,
            'layout': layout,
            'desc': desc,
            'receivers': receivers,
            'create_at': time(),
        }

        self.insert_one(data)


class SenderSESLogsDB(DBBase):
    ''' SenderSESLogsDB Collection '''

    def __init__(self) -> None:
        super().__init__('sender_ses_logs')

    def add(self, cid: str, mail: str, name: str, ses_result: dict[str, Any]) -> None:
        ''' Save log

        :param str cid: cid
        :param str mail: mail
        :param str name: name
        :param dict ses_result: from ses return result

        '''
        data = {
            'cid': cid,
            'mail': mail,
            'name': name,
            'result': ses_result,
            'create_at': time(),
        }

        self.insert_one(data)


class SenderReceiverDB(DBBase):
    ''' SenderReceiver Collection

    :Struct:
        - ``_id``: ObjectID
        - ``cid``: campaign id
        - ``pid``: project id
        - ``data``: data in dict
          - ``mail``: mail and unit
          - ``name``: name
          - (and any other field)

    '''

    def __init__(self) -> None:
        super().__init__('sender_receiver')

    def index(self) -> None:
        ''' Index '''
        self.create_index([('pid', 1), ])
        self.create_index([('data.mail', 1), ])

    @staticmethod
    def new(pid: str, cid: str, name: str, mail: str) -> dict[str, Any]:
        ''' new a struct '''
        return {
            'pid': pid,
            'cid': cid,
            'data': {
                'name': name,
                'mail': mail,
            },
        }

    def remove_past(self, pid: str, cid: str) -> None:
        ''' Remove past data

        - ``cid``: campaign id
        - ``pid``: project id

        '''
        self.delete_many({'pid': pid, 'cid': cid})

    def update_data(self, pid: str, cid: str, datas: list[dict[str, Any]]) -> None:
        ''' Update datas

        - ``cid``: campaign id
        - ``pid``: project id
        - ``datas``: datas

        '''
        for data in datas:
            _data = {}
            for k in data['data']:
                _data[f'data.{k}'] = data['data'][k]

            for key, value in _data.copy().items():
                _data[key] = value.strip()

            self.find_one_and_update(
                {'pid': pid, 'cid': cid, 'data.mail': data['data']['mail']},
                {'$set': _data},
                upsert=True,
            )
