import logging
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.formdb import FormDB
from models.formdb import FormTrafficFeeMappingDB
from module.users import User


class Form(object):
    ''' Form Object '''
    @staticmethod
    def update_appreciation(pid, uid, data):
        ''' Update appreciation

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - available: bool
                - key: ``oauth``, ``badge_name``, ``real_name``
                - value: the name

        '''
        return FormDB().add_by_case(case='appreciation', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_appreciation(pid, uid):
        ''' Get appreciation

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'appreciation', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_appreciation(pid):
        ''' Get all appreciation

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'appreciation', 'pid': pid}):
            yield raw

    @staticmethod
    def update_volunteer_certificate(pid, uid, data):
        ''' Update volunteer certificate

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - value: bool

        '''
        return FormDB().add_by_case(case='volunteer_certificate', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_volunteer_certificate(pid, uid):
        ''' Get volunteer certificate

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'volunteer_certificate', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_volunteer_certificate(pid):
        ''' Get All volunteer certificate

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'volunteer_certificate', 'pid': pid}):
            yield raw

    @staticmethod
    def update_traffic_fee(pid, uid, data):
        ''' Update traffic fee

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - howto: str
                - apply: bool
                - fromwhere: str
                - fee: int

        '''
        return FormDB().add_by_case(case='traffic_fee', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_traffic_fee(pid, uid):
        ''' Get traffic fee

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'traffic_fee', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_traffic_fee(pid):
        ''' Get All traffic_fee

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'traffic_fee', 'pid': pid}):
            yield raw

    @staticmethod
    def update_accommodation(pid, uid, data):
        ''' Update accommodation

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - status: bool
                - key: str, in ('no', 'yes', 'yes-longtraffic')

        '''
        return FormDB().add_by_case(case='accommodation', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_accommodation(pid, uid):
        ''' Get accommodation

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'accommodation', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_accommodation(pid):
        ''' Get all accommodation

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'accommodation', 'pid': pid}):
            yield raw

    @staticmethod
    def update_clothes(pid, uid, data):
        ''' Update clothes

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - clothes: str, 'S / 38.5 / 55'

        '''
        return FormDB().add_by_case(case='clothes', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_clothes(pid, uid):
        ''' Get clothes

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'clothes', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_clothes(pid):
        ''' Get all clothes

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'clothes', 'pid': pid}):
            yield raw

    @staticmethod
    def update_parking_card(pid, uid, data):
        ''' Update parking card

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - carno: str
                - dates: list, ['2020-07-31', ]

        '''
        return FormDB().add_by_case(case='parking_card', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_parking_card(pid, uid):
        ''' Get parking card

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'parking_card', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_parking_card(pid):
        ''' Get all parking card

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'parking_card', 'pid': pid}):
            yield raw


class FormTrafficFeeMapping(object):
    ''' FormTrafficFeeMapping object '''

    @staticmethod
    def save(pid, data):
        ''' Save mapping data

        :param str pid: pid
        :param dict data: location/fee mapping

        '''
        _data = {}
        for location in data:
            _data[location.strip()] = int(data[location])

        return FormTrafficFeeMappingDB().save(pid=pid, data=_data)

    @staticmethod
    def get(pid):
        ''' Get

        :param str pid: pid

        '''
        return FormTrafficFeeMappingDB().find_one({'_id': pid})


class FormAccommodation(object):
    ''' FormAccommodation object '''
    @staticmethod
    def get(pid):
        ''' Get data '''
        for raw in FormDB().find({'case': 'accommodation', 'data.key': {'$ne': 'no'}}):
            yield raw

    @staticmethod
    def update_room(pid, uid, room, change_key=True):
        ''' Update room no

        :param str pid: pid
        :param str uid: uid
        :param str room: room

        '''
        _update = {'data.room': room}
        if change_key:
            _update['data.room_key'] = '%0.8x' % uuid4().fields[0]

        _query = {'case': 'accommodation', 'pid': pid, 'uid': uid}
        _query['$or'] = [{'data.room': {'$ne': room}}, {'data.room': {'$exists': False}}]

        return FormDB().find_one_and_update(
            _query, {'$set': _update},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_room_key(pid, uids):
        ''' update room key '''
        for uid in uids:
            FormDB().find_one_and_update(
                {'case': 'accommodation', 'pid': pid, 'uid': uid}, {'$set': {'data.room_key': '%0.8x' % uuid4().fields[0]}},
            )


    @staticmethod
    def get_room_mate(pid, uid):
        ''' Get room mate

        :param str pid: pid
        :param str uid: uid

        '''
        user_room = FormDB().find_one({'case': 'accommodation', 'pid': pid, 'uid': uid})
        mate = None
        if user_room and 'room' in user_room['data'] and user_room['data']['room']:
            mate = FormDB().find_one(
                {'case': 'accommodation', 'pid': pid, 'uid': {'$ne': uid}, 'data.room': user_room['data']['room']})

        return (user_room, mate)

    @classmethod
    def make_exchange(cls, pid, uid, exkey):
        ''' make exchange

        :param str pid: pid
        :param str uid: uid
        :param str exkey: key

        '''
        data = FormDB().find_one_and_update(
            {'case': 'accommodation', 'pid': pid, 'uid': uid},
            {'$set': {'data.room_exkey': exkey}},
            return_document=ReturnDocument.AFTER,
        )

        ex_mate = FormDB().find_one({'case': 'accommodation', 'pid': pid, 'data.room_exkey': data['data']['room_key']})
        if not ex_mate:
            logging.info(u'等待交換中 %s', exkey)
            return u'等待交換中'

        # do exchange
        new_room = 'R-'+'%0.4x' % uuid4().fields[0]

        FormDB().update_many(
            {'case': 'accommodation', 'pid': pid, 'uid': {'$in': (uid, ex_mate['uid'])}},
            {'$set': {'data.room': new_room}, '$unset': {'data.room_exkey': 1}},
        )

        cls.update_room_key(pid=pid, uids=(uid, ex_mate['uid']))

        logging.info(u'已交換 %s %s %s', new_room, uid, ex_mate['uid'])

        old_mates = list(FormDB().find(
                {'case': 'accommodation', 'pid': pid,
                 'data.room': {'$in': (data['data']['room'], ex_mate['data']['room'])}}))

        logging.info('old_mates: %s', ', '.join([mate['uid'] for mate in old_mates]))

        if len(old_mates) < 2:
            return u'交換完畢'

        uids = [mate['uid'] for mate in old_mates]
        user_infos = User.get_info(uids=uids, need_sensitive=True)
        if user_infos[uids[0]]['profile_real']['roc_id'][1] != user_infos[uids[1]]['profile_real']['roc_id'][1]:
            logging.info(u'old_mates 性別不同，不交換。')
            return u'交換完畢'

        new_room = 'R-'+'%0.4x' % uuid4().fields[0]

        FormDB().update_many(
            {'case': 'accommodation', 'pid': pid, 'uid': {'$in': uids}},
            {'$set': {'data.room': new_room}, '$unset': {'data.room_exkey': 1}},
        )

        cls.update_room_key(pid=pid, uids=uids)

        logging.info('old_mates new rooms: %s, %s', new_room, ', '.join(uids))

        return u'交換完畢'
