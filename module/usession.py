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

    @staticmethod
    def get_no_ipinfo():
        ''' Get no ipinfo '''
        for raw in USessionDB().find({'ipinfo': {'$exists': False}}, {'header.X-Real-Ip': 1, 'header.X-Forwarded-For': 1}):
            yield raw

    @staticmethod
    def update_ipinfo(sid, data):
        ''' Update session ipinfo

        :param str sid: usession id

        '''
        USessionDB().find_one_and_update({'_id': sid}, {'$set': {'ipinfo': data}})
