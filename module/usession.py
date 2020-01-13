from time import time

from models.usessiondb import USessionDB


class USession(object):
    ''' USession Class '''
    @staticmethod
    def make_new(uid, header):
        ''' make new session record

        :param str uid: uid
        :param dict header: headers

        '''
        doc = {'uid': uid, 'header': header, 'created_at': time()}
        return USessionDB().save(doc)

    @staticmethod
    def get(sid):
        ''' Get usession data

        :param str sid: usession id

        '''
        return USessionDB(token=sid).get()
