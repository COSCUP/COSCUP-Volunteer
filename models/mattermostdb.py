from pymongo.collection import ReturnDocument

from models.base import DBBase


class MattermostUsersDB(DBBase):
    ''' MattermostUsersDB Collection

    sync users from Mattermost'''

    def __init__(self):
        super(MattermostUsersDB, self).__init__('mattermost_users')

    def index(self):
        self.create_index([
            ('email', 1),
        ])

    def save(self, data: dict):
        '''save data from fetch get_users api'''
        return self.find_one_and_update(
            {'_id': data['id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
