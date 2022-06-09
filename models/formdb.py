''' FormDB '''
from typing import Any

from pymongo.collection import ReturnDocument

from models.base import DBBase


class FormDB(DBBase):
    ''' Form Collection '''

    def __init__(self) -> None:
        super().__init__('form')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `case`
            - `pid`

        '''
        self.create_index([('case', 1), ])
        self.create_index([('pid', 1), ])

    def add_by_case(self, case: str, pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add data by case

        Args:
            case (str): Case name.
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to insert / update.

        Returns:
            Return the inserted / updated data.

        '''
        _data = {}
        for k in data:
            _data[f'data.{k}'] = data[k]

        return self.find_one_and_update(
            {'case': case, 'pid': pid, 'uid': uid},
            {'$set': _data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )


class FormTrafficFeeMappingDB(DBBase):
    ''' Form traffic fee mapping Collection '''

    def __init__(self) -> None:
        super().__init__('form_traffic_fee_mapping')

    def save(self, pid: str, data: dict[str, Any]) -> dict[str, Any]:  # pylint: disable=arguments-differ
        ''' Save location / fee data

        Args:
            pid (str): Project id.
            data (dict): The data to insert / update.

                Format: `{'{location}': {fee}, ...}`

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': pid},
            {'$set': {'data': data}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
