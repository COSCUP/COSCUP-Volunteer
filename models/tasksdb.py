''' TasksDB '''
from datetime import datetime
from uuid import uuid4

from models.base import DBBase


class TasksDB(DBBase):
    ''' TasksDB Collection '''

    def __init__(self):
        super().__init__('tasks')

    @staticmethod
    def new(pid, body, endtime=None):
        ''' new data '''
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

    def __init__(self):
        super().__init__('tasks_star')

    @staticmethod
    def new(pid, uid):
        ''' new data '''
        return {
            'pid': pid,
            'uid': uid,
            'created_at': datetime.now(),
        }
