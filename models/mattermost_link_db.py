from models.base import DBBase


class MattermostLinkDB(DBBase):
    ''' MattermostLinkDB Collection

    struct:
        - _id: uid
        - code: uuid4 ...
        - data: mattermost request data
        - create_at: int

    '''
    def __init__(self):
        super(MattermostLinkDB, self).__init__('mattermost_link')

    def index(self):
        ''' Index '''
        self.create_index([('data.user_name', 1), ])
