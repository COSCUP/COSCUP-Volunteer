from typing import Any
from uuid import uuid4
from datetime import datetime

from models.base import DBBase


class TasksDB(DBBase):
    ''' TasksDB Collection '''

    def __init__(self):
        super(TasksDB, self).__init__('tasks')

    @staticmethod
    def new(pid: str,
            title: str,
            cate: str,
            desc: str,
            limit: int,
            starttime: Any,
            created_by: str,
            endtime: str | None = None):
        return {
            '_id': '%0.8x' % uuid4().fields[0],
            'pid': pid,
            'title': title,
            'cate': cate,
            'desc': desc,
            'limit': limit,
            'people': [],
            'starttime': starttime,
            'endtime': endtime,
            'created_by': created_by,
            'created_at': datetime.now(),
        }


class TasksStarDB(DBBase):
    ''' TasksStarDB Collection '''

    def __init__(self):
        super(TasksStarDB, self).__init__('tasks_star')

    @staticmethod
    def new(pid: str, uid: str):
        return {
            'pid': pid,
            'uid': uid,
            'created_at': datetime.now(),
        }
