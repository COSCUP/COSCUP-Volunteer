''' MattermostLinkDB '''
from models.base import DBBase


class MattermostLinkDB(DBBase):
    ''' MattermostLinkDB Collection

    Struct:
        - ``_id``: User id.
        - ``code``: Random code for the user to verify in Mattermost.
        - ``data``: `dict` User info data from Mattermost.
        - ``create_at``: `timestamp`

    '''

    def __init__(self) -> None:
        super().__init__('mattermost_link')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `data.user_id`
            - `data.user_name`

        '''
        self.create_index([('data.user_id', 1), ])
        self.create_index([('data.user_name', 1), ])
