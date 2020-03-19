from time import time
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

        - ``mail``:
            - ``subject``: subject
            - ``content``: content, support markdown

    '''

    def __init__(self):
        super(SenderCampaignDB, self).__init__('sender_campaign')

    @staticmethod
    def new(name, pid, tid, uid):
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
            },
            'mail': {
                'subject': '',
                'content': '',
                'preheader': '',
                'layout': '1',
            },
        }

    def save(self, data):
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


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

    def __init__(self):
        super(SenderReceiverDB, self).__init__('sender_receiver')

    def index(self):
        ''' Index '''
        self.create_index([('pid', 1), ])
        self.create_index([('data.mail', 1), ])

    @staticmethod
    def new(pid, cid, name, mail):
        ''' new a struct '''
        return {
            'pid': pid,
            'cid': cid,
            'data': {
                'name': name,
                'mail': mail,
            },
        }

    def remove_past(self, pid, cid):
        ''' Remove past data

        - ``cid``: campaign id
        - ``pid``: project id

        '''
        self.delete_many({'pid': pid, 'cid': cid})

    def update_data(self, pid, cid, datas):
        ''' Update datas

        - ``cid``: campaign id
        - ``pid``: project id
        - ``datas``: datas

        '''
        for data in datas:
            _data = {}
            for k in data['data']:
                _data['data.%s' % k] = data['data'][k]

            for k in _data:
                _data[k] = _data[k].strip()

            self.find_one_and_update(
                {'pid': pid, 'cid': cid, 'data.mail': data['data']['mail']},
                {'$set': _data},
                upsert=True,
            )
