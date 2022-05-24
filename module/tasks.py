''' Task '''
from datetime import datetime
from typing import Any, Generator, Optional

from pymongo.collection import ReturnDocument
from pymongo.results import DeleteResult

from models.tasksdb import TasksDB, TasksStarDB
from module.users import User


class Tasks:
    ''' Tasks class '''

    @classmethod
    def add(cls, pid: str, body: dict[str, Any],
            endtime: Optional[datetime] = None, task_id: Optional[str] = None) -> dict[str, Any]:
        ''' add new task

        :param str pid: pid
        :param dict body: body
        :param str title: title
        :param str cate: cate
        :param str desc: description
        :param int limit: user limit
        :param datetime starttime: start datetime
        :param datetime endtime: end datetime
        :param str created_by: uid
        :param str task_id: task id

        '''
        data = TasksDB.new(pid=pid, body=body, endtime=endtime)

        if task_id is not None:
            if not cls.get_with_pid(pid=pid, _id=task_id):
                raise Exception(f'No task_id: {task_id}')

            data['_id'] = task_id
            data.pop('people', None)
            data.pop('created_by', None)
            data.pop('created_at', None)

        return TasksDB().find_one_and_update(
            {'_id': data['_id'], 'pid': data['pid']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def delete(pid: str, _id: str) -> None:
        ''' Del task '''
        TasksDB().delete_one({'_id': _id, 'pid': pid})

    @staticmethod
    def get_by_pid(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get by pid

        :param str pid: pid

        '''
        for raw in TasksDB().find({'pid': pid}, sort=(('starttime', 1), )):
            yield raw

    @staticmethod
    def get_with_pid(pid: str, _id: str) -> Optional[dict[str, Any]]:
        ''' Get with pid '''
        return TasksDB().find_one({'pid': pid, '_id': _id})

    @staticmethod
    def get_cate(pid: str) -> list[dict[str, Any]]:
        ''' Get cate '''
        cates = TasksDB().find({'pid': pid}).distinct('cate')
        return [cate for cate in cates if cate]

    @staticmethod
    def join(pid: str, task_id: str, uid: str) -> dict[str, Any]:
        ''' Join to '''
        return TasksDB().find_one_and_update(
            {'_id': task_id, 'pid': pid},
            {'$addToSet': {'people': uid}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def cancel(pid: str, task_id: str, uid: str) -> dict[str, Any]:
        ''' cancel join '''
        return TasksDB().find_one_and_update(
            {'_id': task_id, 'pid': pid},
            {'$pull': {'people': uid}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_peoples_info(pid: str, task_id: str) -> Optional[dict[str, Any]]:
        ''' Get peoples info '''
        task = TasksDB().find_one(
            {'pid': pid, '_id': task_id}, {'people': 1})

        if task:
            uids = task['people']
            return User.get_info(uids=uids)

        return None


class TasksStar:
    ''' TasksStar object '''

    @staticmethod
    def add(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' add '''
        data = TasksStarDB().find_one({'pid': pid, 'uid': uid})
        if not data:
            TasksStarDB().insert_one(TasksStarDB.new(pid=pid, uid=uid))
            data = TasksStarDB().find_one({'pid': pid, 'uid': uid})

        return data

    @staticmethod
    def delete(pid: str, uid: str) -> DeleteResult:
        ''' delete '''
        return TasksStarDB().delete_one({'pid': pid, 'uid': uid})

    @staticmethod
    def status(pid: str, uid: str) -> dict[str, bool]:
        ''' ststus '''
        if TasksStarDB().find_one({'pid': pid, 'uid': uid}):
            return {'add': True}

        return {'add': False}

    @staticmethod
    def toggle(pid: str, uid: str) -> dict[str, bool]:
        ''' toggle '''
        data = TasksStarDB().find_one({'pid': pid, 'uid': uid})
        if data:
            TasksStarDB().delete_one({'pid': pid, 'uid': uid})
            return {'add': False}

        TasksStarDB().insert_one(TasksStarDB.new(pid=pid, uid=uid))
        return {'add': True}

    @staticmethod
    def get(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all star users '''
        for user in TasksStarDB().find({'pid': pid}, {'uid': 1}):
            yield user
