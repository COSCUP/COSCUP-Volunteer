from pymongo.collection import ReturnDocument

from models.tasksdb import TasksDB


class Tasks(object):
    ''' Tasks class '''

    @staticmethod
    def add(pid, title, cate, desc, limit, starttime, created_by, endtime=None, task_id=None):
        ''' add new task

        :param str pid: pid
        :param str title: title
        :param str cate: cate
        :param str desc: description
        :param int limit: user limit
        :param datetime starttime: start datetime
        :param datetime endtime: end datetime
        :param str created_by: uid
        :param str task_id: task id

        '''
        data = TasksDB.new(
            pid=pid, title=title, cate=cate, desc=desc, limit=limit,
            starttime=starttime, created_by=created_by, endtime=endtime)

        if task_id is not None:
            data['task_id'] = task_id

        return TasksDB().find_one_and_update(
            {'_id': data['_id'], 'pid': data['pid']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def get_by_pid(pid):
        ''' Get by pid

        :param str pid: pid

        '''
        for raw in TasksDB().find({'pid': pid}, sort=(('starttime', 1), )):
            yield raw

    @staticmethod
    def get_cate(pid):
        ''' Get cate '''
        return TasksDB().find({'pid': pid}).distinct('cate')

    @staticmethod
    def join(pid, task_id, uid):
        ''' Join to '''
        return TasksDB().find_one_and_update(
            {'_id': task_id, 'pid': pid},
            {'$addToSet': {'people': uid}},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def cancel(pid, task_id, uid):
        ''' cancel join '''
        return TasksDB().find_one_and_update(
            {'_id': task_id, 'pid': pid},
            {'$pull': {'people': uid}},
            return_document=ReturnDocument.AFTER,
        )
