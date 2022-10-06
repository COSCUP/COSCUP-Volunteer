''' Sender DB '''
from time import time
from typing import Any
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class SenderCampaignDB(DBBase):
    ''' SenderCampaign Collection '''

    def __init__(self) -> None:
        super().__init__('sender_campaign')

    @staticmethod
    def new(name: str, pid: str, tid: str, uid: str) -> dict[str, Any]:
        ''' new a default struct

        Args:
            name (str): Campaign name.
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.

        Returns:
            Return a default struct.

        Struct:
            - ``_id``: Unique id, or `cid`.
            - ``name``: Campaign name.
            - ``created``:
                - ``pid``: Project id.
                - ``tid``: Team id.
                - ``uid``: User id.
                - ``at``: Created at.
            - ``receiver``:
                - ``teams``: List of team id(`tid`)
                - ``users``: List of user id(`uid)
                - ``team_w_tags``: List of the tag id created by team.
                - ``all_users``: `bool` Is send to all platform's users.

            - ``mail``:
                - ``subject``: Subject.
                - ``content``: Content, and Markdown format supported.

        TODO:
            Need refactor in pydantic.

        '''
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
        ''' Save data

        Args:
            data (dict): The data to insert / update.

        Returns:
            Return the inserted / updated data.

        '''
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

        Args:
            cid (str): Campaign id, the `id` is from [models.senderdb.SenderCampaignDB][].
            layout (str): In `1`, `2`.
            desc (str): Description.
            receivers (list): List of user info or replace data. Required fields in `name`, `mail`.

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

        Args:
            cid (str): Campaign id, the `id` is from [models.senderdb.SenderCampaignDB][].
            mail (str): User mail.
            name (str): User name.
            ses_result (str): The result from the return of
                              [SES.Client.send_email][] / [SES.Client.send_raw_email][].

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

    For User to upload the list of receivers in CSV.

    '''

    def __init__(self) -> None:
        super().__init__('sender_receiver')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`
            - `data.mail`

        '''
        self.create_index([('pid', 1), ])
        self.create_index([('data.mail', 1), ])

    @staticmethod
    def new(pid: str, cid: str, name: str, mail: str) -> dict[str, Any]:
        ''' new a struct

        Args:
            pid (str): Project id.
            cid (str): Campaign id, the `id` is from [models.senderdb.SenderCampaignDB][].
            mail (str): User's mail.
            name (str): User name.

        Returns:
            Return a default struct.

        Struct:
            - ``_id``: Random id in `ObjectID`.
            - ``cid``: Campaign id
            - ``pid``: Project id
            - ``data``: `dict`
                - ``mail``: User mail.
                - ``name``: User name.
                - ``...``: *(... and any other fields.)*

        TODO:
            Need refactor in pydantic.

        '''
        return {
            'pid': pid,
            'cid': cid,
            'data': {
                'name': name,
                'mail': mail,
            },
        }

    def remove_past(self, pid: str, cid: str) -> int:
        ''' Remove past data

        Args:
            pid (str): Project id.
            cid (str): Campaign id, the `id` is from [models.senderdb.SenderCampaignDB][].

        '''
        return self.delete_many({'pid': pid, 'cid': cid}).deleted_count

    def update_data(self, pid: str, cid: str, datas: list[dict[str, Any]]) -> None:
        ''' Update datas

        Args:
            pid (str): Project id.
            cid (str): Campaign id, the `id` is from [models.senderdb.SenderCampaignDB][].
            datas (list): List of data to inserted / updated. Must have `mail`, `name`.

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
