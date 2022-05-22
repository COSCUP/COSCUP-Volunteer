''' DB base '''
from time import time
from typing import TYPE_CHECKING, Any

import setting

if not setting.MONGO_MOCK:
    from pymongo.collection import Collection
    from pymongo.mongo_client import MongoClient
    MOCK_DB_STORE = None
else:
    import mongomock
    from mongomock.collection import Collection  # type: ignore
    from mongomock.store import DatabaseStore
    MOCK_DB_STORE = DatabaseStore()  # type: ignore

if TYPE_CHECKING:
    class DBBase(Collection[dict[str, Any]]):
        ''' DBBase '''
        # pylint: disable=super-init-not-called,multiple-statements

        def __init__(self, name: str) -> None: ...

else:
    class DBBase(Collection):  # pylint: disable=abstract-method
        ''' DBBase class

        :param str name: collection name

        '''

        def __init__(self, name: str) -> None:
            if not setting.MONGO_MOCK:
                client = MongoClient(
                    f'mongodb://{setting.MONGO_HOST}:{setting.MONGO_PORT}')[setting.MONGO_DBNAME]
                super_args = {'database': client, 'name': name}
            else:
                client = mongomock.MongoClient()['testing']
                super_args = {'database': client, 'name': name,
                              '_db_store': MOCK_DB_STORE}

            super().__init__(**super_args)

        @staticmethod
        def make_create_at(data: dict[str, Any]) -> None:
            ''' make create_at timestamp

            :param dict data: data

            '''
            data['created_at'] = time()
