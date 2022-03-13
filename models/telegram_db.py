from typing import Any
from pymongo.collection import ReturnDocument

from models.base import DBBase


class TelegramDB(DBBase):
    ''' TelegramDB Collection '''
    def __init__(self):
        super(TelegramDB, self).__init__('telegram')

    def index(self):
        self.create_index([('uid', 1), ])

    def save(self, data: Any):
        self.find_one_and_update(
                {'_id': data['id']},
                {'$set': data},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

