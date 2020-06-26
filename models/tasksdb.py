from uuid import uuid4
from datetime import datetime

from models.base import DBBase


class TasksDB(DBBase):
    ''' TasksDB Collection '''
    def __init__(self):
        super(TasksDB, self).__init__('tasks')

    @staticmethod
    def new(pid, title, cate, desc, limit, starttime, created_by, endtime=None):
        ''' new data '''
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
