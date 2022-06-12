''' MC '''
import pylibmc  # type: ignore
from pylibmc import Client

import setting


class MC:  # pylint: disable=too-few-public-methods
    ''' Memcached cache '''
    @staticmethod
    def get_client() -> Client:
        ''' Get client

        - `binary`: `True`.
        - `behaviors`:
            - `tcp_nodelay`: `True`
            - `ketama`: `True`

        Returns:
            [pylibmc.Client][]

        '''
        return pylibmc.Client(setting.MC_SERVERS,
                              binary=True,
                              behaviors={'tcp_nodelay': True, 'ketama': True})
