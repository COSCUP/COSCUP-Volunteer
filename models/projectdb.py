''' ProjectDB '''
from typing import Any

from pymongo.collection import ReturnDocument

from models.base import DBBase


class ProjectDB(DBBase):
    ''' Project Collection

    :Struct:
        - ``_id``: project id (pid)
        - ``name``: show name
        - ``action_date``: timestamp
        - ``owners``: list of uid

    '''

    def __init__(self, pid: str) -> None:
        super().__init__('project')
        self.pid = pid

    def index(self) -> None:
        ''' Index '''
        self.create_index([('owners', 1), ('action_date', -1)])

    def default(self) -> dict[str, Any]:
        ''' default data '''
        result = {
            '_id': self.pid,
            'name': '',
            'action_date': 0,
            'desc': '',
            'owners': [],
        }
        self.make_create_at(result)
        return result

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add data

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
