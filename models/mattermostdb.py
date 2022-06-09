''' MattermostUsersDB '''
from typing import Any

from pymongo.collection import ReturnDocument

from models.base import DBBase


class MattermostUsersDB(DBBase):
    ''' MattermostUsersDB Collection

    Sync user datas from Mattermost for mapping.

    '''

    def __init__(self) -> None:
        super().__init__('mattermost_users')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `email`

        '''
        self.create_index([('email', 1), ])

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Save data from `/users` api

        Args:
            data (dict): The data responsed from api.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': data['id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
