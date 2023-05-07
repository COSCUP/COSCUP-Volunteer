''' Task '''
from typing import Any, Generator, Optional

from pymongo.collection import ReturnDocument
from pymongo.results import DeleteResult

from models.tasksdb import TasksDB, TasksStarDB
from module.users import User


class Tasks:
    ''' Tasks class '''

    @classmethod
    def add(cls, pid: str, body: dict[str, Any]) -> dict[str, Any]:
        ''' add new task

        Args:
            pid (str): Project id.
            body (dict): The data to add.

                - `title`: Task title.
                - `cate`: Take category.
                - `desc`: Description.
                - `limit`: `int` User limit.
                - `starttime`: Start time in ISO8601.

        '''
        data = body

        if cls.get_with_pid(pid=pid, _id=data['_id']):
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
        ''' Del task

        Args:
            pid (str): Project id.
            _id (str): task unique id.

        '''
        TasksDB().delete_one({'_id': _id, 'pid': pid})

    @staticmethod
    def get_by_pid(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get by pid

        Args:
            pid (str): Project id.

        Yields:
            Yield return the data.

        '''
        for raw in TasksDB().find({'pid': pid}, sort=(('starttime', 1), )):
            yield raw

    @staticmethod
    def get_with_pid(pid: str, _id: str) -> Optional[dict[str, Any]]:
        ''' Get with pid

        Args:
            pid (str): Project id.
            _id (str): task unique id.

        Returns:
            Return the data.

        '''
        return TasksDB().find_one({'pid': pid, '_id': _id})

    @staticmethod
    def get_cate(pid: str) -> list[dict[str, Any]]:
        ''' Get cate

        Args:
            pid (str): Project id.

        Returns:
            Return the datas.

        '''
        cates = TasksDB().find({'pid': pid}).distinct('cate')
        return [cate for cate in cates if cate]

    @staticmethod
    def join(pid: str, task_id: str, uid: str) -> dict[str, Any]:
        ''' Join to

        Args:
            pid (str): Project id.
            task_id (str): Task id.
            uid (str): User id.

        Returns:
            Return the added data.

        '''
        return TasksDB().find_one_and_update(
            {'_id': task_id, 'pid': pid},
            {'$addToSet': {'people': uid}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def cancel(pid: str, task_id: str, uid: str) -> dict[str, Any]:
        ''' cancel join

        Args:
            pid (str): Project id.
            task_id (str): Task id.
            uid (str): User id.

        Returns:
            Return the updated data.

        '''
        return TasksDB().find_one_and_update(
            {'_id': task_id, 'pid': pid},
            {'$pull': {'people': uid}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_peoples_info(pid: str, task_id: str) -> Optional[dict[str, Any]]:
        ''' Get peoples info

        Args:
            pid (str): Project id.
            task_id (str): Task id.

        Returns:
            Return the datas.

        '''
        task = TasksDB().find_one(
            {'pid': pid, '_id': task_id}, {'people': 1})

        if task:
            uids = task['people']
            return User.get_info(uids=uids)

        return None

    @staticmethod
    def sitemap() -> list[str]:
        ''' list sitemap paths '''
        pid = set()
        paths: list[str] = []
        for task in TasksDB().find():
            pid.add(task['pid'])
            paths.append(f"/tasks/{task['pid']}/r/{task['_id']}")

        for year in pid:
            paths.append(f"/tasks/{year}")

        return paths


class TasksStar:
    ''' TasksStar object '''

    @staticmethod
    def add(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' add

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            Return the data.

        '''
        data = TasksStarDB().find_one({'pid': pid, 'uid': uid})
        if not data:
            TasksStarDB().insert_one(TasksStarDB.new(pid=pid, uid=uid))
            data = TasksStarDB().find_one({'pid': pid, 'uid': uid})

        return data

    @staticmethod
    def delete(pid: str, uid: str) -> DeleteResult:
        ''' delete

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            Return the delete result in [pymongo.results.DeleteResult][].

        '''
        return TasksStarDB().delete_one({'pid': pid, 'uid': uid})

    @staticmethod
    def status(pid: str, uid: str) -> dict[str, bool]:
        ''' ststus

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            `{'add': <bool>}`

        '''
        if TasksStarDB().find_one({'pid': pid, 'uid': uid}):
            return {'add': True}

        return {'add': False}

    @staticmethod
    def toggle(pid: str, uid: str) -> dict[str, bool]:
        ''' toggle

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            `{'add': <bool>}`

        '''
        data = TasksStarDB().find_one({'pid': pid, 'uid': uid})
        if data:
            TasksStarDB().delete_one({'pid': pid, 'uid': uid})
            return {'add': False}

        TasksStarDB().insert_one(TasksStarDB.new(pid=pid, uid=uid))
        return {'add': True}

    @staticmethod
    def get(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all star users

        Args:
            pid (str): Project id.

        Yields:
            Return the datas.

        '''
        for user in TasksStarDB().find({'pid': pid}, {'uid': 1}):
            yield user
