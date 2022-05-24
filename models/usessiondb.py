''' USessionDB '''
import hashlib
from time import time
from typing import Any, Optional
from uuid import uuid4

from pymongo.results import InsertOneResult

from models.base import DBBase


class USessionDB(DBBase):
    ''' USessionDB Collection '''

    def __init__(self, token: Optional[str] = None) -> None:
        super().__init__('usession')

        if token is None:
            message = hashlib.sha256()
            message.update((f'{uuid4().hex}{time()}').encode('utf8'))
            token = message.hexdigest()

        self.token = token

    def index(self) -> None:
        ''' Index '''
        self.create_index([('created_at', 1), ])
        self.create_index([('ipinfo', 1), ])
        self.create_index([('uid', 1), ])
        self.create_index([('alive', 1), ])

    def add(self, data: dict[str, Any]) -> InsertOneResult:
        ''' save

        :param dict data: data

        '''
        doc = {}
        doc.update(data)
        doc['_id'] = self.token

        return self.insert_one(doc)

    def get(self) -> Optional[dict[str, Any]]:
        ''' Get data '''
        return self.find_one({'_id': self.token, 'alive': True})
