''' TelegramDB '''
from typing import Any

from pymongo.collection import ReturnDocument

from models.base import DBBase


class TelegramDB(DBBase):
    ''' TelegramDB Collection '''

    def __init__(self) -> None:
        super().__init__('telegram')

    def index(self) -> None:
        ''' Index '''
        self.create_index([('uid', 1), ])

    def add(self, data: dict[str, Any]) -> None:
        ''' save data '''
        self.find_one_and_update(
            {'_id': data['id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
