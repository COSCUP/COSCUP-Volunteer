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

    def __init__(self, pid):
        super(ProjectDB, self).__init__('project')
        self.pid = pid

    def index(self):
        self.create_index([('owners', 1), ('action_date', -1)])

    def default(self):
        r = {
            '_id': self.pid,
            'name': '',
            'action_date': 0,
            'desc': '',
            'owners': [],
        }
        self.make_create_at(r)
        return r

    def add(self, data: dict):
        '''Add data'''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
