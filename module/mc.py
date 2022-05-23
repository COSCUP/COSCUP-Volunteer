''' MC '''
import pylibmc
from pylibmc import Client

import setting


class MC:  # pylint: disable=too-few-public-methods
    ''' Memcached cache '''
    @staticmethod
    def get_client() -> Client:
        ''' Get client '''
        return pylibmc.Client(setting.MC_SERVERS,
                              binary=True,
                              behaviors={'tcp_nodelay': True, 'ketama': True})
