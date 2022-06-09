''' TelegramDB '''
from typing import Any

from pymongo.collection import ReturnDocument

from models.base import DBBase


class TelegramDB(DBBase):
    ''' TelegramDB Collection '''

    def __init__(self) -> None:
        super().__init__('telegram')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `uid`, `uid`

        '''
        self.create_index([('uid', 1), ])

    def add(self, data: dict[str, Any]) -> None:
        ''' save data

        Args:
            data (dict): The data to insert / update.

        The data's struct

        Struct:
            - `_id`: telegram id.
            - `added`: Added time in datatime.
            - `first_name`: First name.
            - `id`: telegram id.
            - `is_bot`: `bool`.
            - `language_code`: Language in ISO 639.
            - `uid`: Mapping to our user id.
            - `username`: User name.

        TODO:
            Need refactor in pydantic.

        '''
        self.find_one_and_update(
            {'_id': data['id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
