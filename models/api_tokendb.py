''' API Token DB '''
from models.base import DBBase


class APITokenDB(DBBase):  # pylint: disable=abstract-method
    ''' APITokenDB Collection '''

    def __init__(self) -> None:
        super().__init__('api_token')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `token_type`, `alive`, `username`
            - `token_type`, `alive`, `serial_no`

        '''
        self.create_index([('alive', 1), ('token_type', 1), ('username', 1)])
        self.create_index([('alive', 1), ('token_type', 1), ('serial_no', 1)])
