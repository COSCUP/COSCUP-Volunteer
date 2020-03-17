from time import time
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.base import DBBase


class SenderCampaignDB(DBBase):
    ''' SenderCampaign Collection

    :Struct:
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
