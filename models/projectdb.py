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
        ''' Index '''
        self.create_index([('owners', 1), ])

    def default(self):
        ''' default data '''
        r = {
            '_id': self.pid,
            'name': '',
            'action_date': 0,
            'owners': [],
        }
        self.make_create_at(r)
        return r

    def add(self, data):
        ''' Add data

        :param dict data: data

        '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
