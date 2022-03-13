from time import time

from pymongo.collection import ReturnDocument

from models.base import DBBase


class MailLetterDB(DBBase):
    ''' MailLetterDB Collection '''
    def __init__(self):
        super(MailLetterDB, self).__init__('mailletter')

    def index(self):
        self.create_index([('code.welcome', 1), ])

    def create(self, uid: str):
        ''' Add user into sendlist'''
        self.find_one_and_update({'_id': uid}, {'$set': {'create_at': time()}}, upsert=True)

    def is_sent(self, uid: str, code: str) -> float:
        ''' Check if it is sent or not'''
        raw = self.find_one({'_id': uid}, {'code.%s' % code: 1})
        if raw and 'code' in raw and code in raw['code']:
            return raw['code'][code]

        return 0

    def make_sent(self, uid: str, code: str) -> dict:
        '''Make sent

        :return: raw data'''
        return self.find_one_and_update(
            {'_id': uid},
            {'$set': {'code.%s' % code: time()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    def need_to_send(self, code: str):
        ''' Find need to send list'''
        for raw in self.find({'code.%s' % code: {'$exists': False}}):
            yield raw
