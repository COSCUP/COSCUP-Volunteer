import pylibmc

import setting


class MC(object):

    @staticmethod
    def get_client():
        return pylibmc.Client(setting.MC_SERVERS,
                              binary=True,
                              behaviors={
                                  "tcp_nodelay": True,
                                  "ketama": True
                              })
