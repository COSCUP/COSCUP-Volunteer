''' TasksDB '''
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from models.base import DBBase


class TasksDB(DBBase):
    ''' TasksDB Collection '''

    def __init__(self) -> None:
        super().__init__('tasks')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`

        '''
        self.create_index([('pid', -1), ])

    @staticmethod
    def new(pid: str, body: dict[str, Any], endtime: Optional[datetime] = None) -> dict[str, Any]:
        ''' new data

        Args:
            pid (str): Project id.
            body (dict): The data must have `title`, `cate`, `desc`, `limit`,
                         `starttime`, `created_by`.
            endtime (datetime): Optional, The end datetime.

        Returns:
            Return a default struct.

        Struct:
            - ``_id``: Unique task id.
            - ``pid``: Project id.
            - ``title``: Task title.
            - ``cate``: Category, any strings by user's definitions.
            - ``desc``: Description.
            - ``limit``: `int` The max numbers of users.
            - ``people``: List of user id. (They will join into)
            - ``starttime``: The [datetime.datetime][] of when to start.
            - ``endtime``: The [datetime.datetime][] in the end.
            - ``created_by``: Created by who in user id.
            - ``created_at``: Created at in [datetime.datetime][].

        TODO:
            Need refactor in pydantic.

        '''
        return {
            '_id': f'{uuid4().fields[0]:08x}',
            'pid': pid,
            'title': body['title'],
            'cate': body['cate'],
            'desc': body['desc'],
            'limit': body['limit'],
            'people': [],
            'starttime': body['starttime'],
            'endtime': endtime,
            'created_by': body['created_by'],
            'created_at': datetime.now(),
        }


class TasksStarDB(DBBase):
    ''' TasksStarDB Collection '''

    def __init__(self) -> None:
        super().__init__('tasks_star')

    @staticmethod
    def new(pid: str, uid: str) -> dict[str, Any]:
        ''' new data

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            Return a default struct.

        Struct:
            - ``pid``: Project id.
            - ``uid``: User id.
            - ``created_at``: Created at in [datetime.datetime][].

        TODO:
            Need refactor in pydantic.

        '''
        return {
            'pid': pid,
            'uid': uid,
            'created_at': datetime.now(),
        }
