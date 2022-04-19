''' MailLetterDB '''
from time import time

from pymongo.collection import ReturnDocument

from models.base import DBBase


class MailLetterDB(DBBase):
    ''' MailLetterDB Collection '''

    def __init__(self):
        super().__init__('mailletter')

    def index(self):
        ''' Index '''
        self.create_index([('code.welcome', 1), ])

    def create(self, uid):
        ''' Add user into sendlist

        :param str uid: user id

        '''
        self.find_one_and_update(
            {'_id': uid}, {'$set': {'create_at': time()}}, upsert=True)

    def is_sent(self, uid, code):
        ''' Check is sent or not

        :param str uid: user id
        :param str code: code
        :rtype: float

        '''
        raw = self.find_one({'_id': uid}, {f'code.{code}': 1})
        if raw and 'code' in raw and code in raw['code']:
            return raw['code'][code]

        return 0

    def make_sent(self, uid, code):
        ''' Make sent

        :param str uid: user id
        :param str code: code
        :rtype: dict
        :return: return raw data

        '''
        return self.find_one_and_update(
            {'_id': uid},
            {'$set': {f'code.{code}': time()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def need_to_send(self, code):
        ''' Find need to send list

        :param str code: code

        '''
        for raw in self.find({f'code.{code}': {'$exists': False}}):
            yield raw
