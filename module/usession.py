from time import time

from models.usessiondb import USessionDB
from module.mc import MC


class USession(object):
    ''' USession Class '''
    @staticmethod
    def make_new(uid, header):
        ''' make new session record

        :param str uid: uid
        :param dict header: headers

        '''
        doc = {'uid': uid, 'header': header, 'created_at': time(), 'alive': True}
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

    @staticmethod
    def get_recently(uid, limit=25):
        ''' Get recently record

        :param str uid: uid

        '''
        for raw in USessionDB(token='').find({'uid': uid}, sort=(('created_at', -1), ), limit=limit):
            yield raw

    @staticmethod
    def get_alive(uid):
        ''' Get alive session

        :param str uid: uid

        '''
        for raw in USessionDB(token='').find({'uid': uid, 'alive': True}):
            yield raw

    @staticmethod
    def make_dead(sid, uid=None):
        if uid is None:
            USessionDB(token='').find_one_and_update({'_id': sid}, {'$set': {'alive': False}})
            MC.get_client().delete('sid:%s' % sid)
        else:
            if USessionDB(token='').find_one_and_update({'_id': sid, 'uid': uid}, {'$set': {'alive': False}}):
                MC.get_client().delete('sid:%s' % sid)
