''' API Token DB '''
from models.base import DBBase


class APITokenDB(DBBase):  # pylint: disable=abstract-method
    ''' APITokenDB Collection '''

    def __init__(self) -> None:
        super().__init__('api_token')
