''' Form '''
import logging
from collections.abc import Iterable
from typing import Any, Generator, Optional
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.formdb import FormDB, FormTrafficFeeMappingDB
from module.users import User


class Form:  # pylint: disable=too-many-public-methods
    ''' Form Object '''
    @staticmethod
    def update_appreciation(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
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
    def get_appreciation(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get appreciation

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'appreciation', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_appreciation(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all appreciation

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'appreciation', 'pid': pid}):
            yield raw

    @staticmethod
    def update_volunteer_certificate(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
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
    def get_volunteer_certificate(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get volunteer certificate

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'volunteer_certificate', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_volunteer_certificate(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get All volunteer certificate

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'volunteer_certificate', 'pid': pid}):
            yield raw

    @staticmethod
    def update_traffic_fee(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
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
    def get_traffic_fee(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get traffic fee

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'traffic_fee', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_traffic_fee(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get All traffic_fee

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'traffic_fee', 'pid': pid}):
            yield raw

    @staticmethod
    def update_accommodation(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
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
    def get_accommodation(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get accommodation

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'accommodation', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_accommodation(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all accommodation

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'accommodation', 'pid': pid}):
            yield raw

    @staticmethod
    def update_clothes(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
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
    def get_clothes(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get clothes

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'clothes', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_clothes(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all clothes

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'clothes', 'pid': pid}):
            yield raw

    @staticmethod
    def update_parking_card(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
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
    def get_parking_card(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get parking card

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'parking_card', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_parking_card(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all parking card

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'parking_card', 'pid': pid}):
            yield raw

    @staticmethod
    def update_drink(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update drink

        :param str pid: project id
        :param str uid: user id
        :param dict data: form data

        .. note::
            - data:
                - y18: bool

        '''
        return FormDB().add_by_case(case='drink', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_drink(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get drink

        :param str pid: project id
        :param str uid: user id

        '''
        return FormDB().find_one({'case': 'drink', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_drink(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all drink

        :param str pid: project id

        '''
        for raw in FormDB().find({'case': 'drink', 'pid': pid}):
            yield raw


class FormTrafficFeeMapping:
    ''' FormTrafficFeeMapping object '''

    @staticmethod
    def save(pid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Save mapping data

        :param str pid: pid
        :param dict data: location/fee mapping

        '''
        _data = {}
        for location in data:
            _data[location.strip()] = int(data[location])

        return FormTrafficFeeMappingDB().save(pid=pid, data=_data)

    @staticmethod
    def get(pid: str) -> Optional[dict[str, Any]]:
        ''' Get

        :param str pid: pid

        '''
        return FormTrafficFeeMappingDB().find_one({'_id': pid})


class FormAccommodation:
    ''' FormAccommodation object '''
    @staticmethod
    def get(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get data '''
        for raw in FormDB().find({'case': 'accommodation', 'pid': pid, 'data.key': {'$ne': 'no'}}):
            yield raw

    @staticmethod
    def update_room(pid: str, uid: str, room: str, change_key: bool = True) -> dict[str, Any]:
        ''' Update room no

        :param str pid: pid
        :param str uid: uid
        :param str room: room

        '''
        _update = {'data.room': room}
        if change_key:
            _update['data.room_key'] = f'{uuid4().fields[0]:08x}'

        _query: dict[str, Any]
        _query = {'case': 'accommodation', 'pid': pid, 'uid': uid}
        _query['$or'] = [{'data.room': {'$ne': room}},
                         {'data.room': {'$exists': False}}]

        return FormDB().find_one_and_update(
            _query, {'$set': _update},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def update_room_key(pid: str, uids: Iterable[str]) -> None:
        ''' update room key '''
        for uid in uids:
            FormDB().find_one_and_update(
                {'case': 'accommodation', 'pid': pid, 'uid': uid}, {
                    '$set': {'data.room_key': f'{uuid4().fields[0]:08x}'}},
            )

    @staticmethod
    def get_room_mate(pid: str, uid: str) -> \
            tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        ''' Get room mate

        :param str pid: pid
        :param str uid: uid

        '''
        user_room = FormDB().find_one(
            {'case': 'accommodation', 'pid': pid, 'uid': uid})
        mate = None
        if user_room and 'room' in user_room['data'] and user_room['data']['room']:
            mate = FormDB().find_one(
                {'case': 'accommodation', 'pid': pid,
                 'uid': {'$ne': uid}, 'data.room': user_room['data']['room']})

        return (user_room, mate)

    @classmethod
    def make_exchange(cls, pid: str, uid: str, exkey: str) -> str:
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

        ex_mate = FormDB().find_one(
            {'case': 'accommodation', 'pid': pid, 'data.room_exkey': data['data']['room_key']})
        if not ex_mate:
            logging.info('等待交換中 `%s`', exkey)
            return '等待交換中'

        # do exchange
        new_room = 'R-'+f'{uuid4().fields[0]:04x}'

        FormDB().update_many(
            {'case': 'accommodation', 'pid': pid,
                'uid': {'$in': (uid, ex_mate['uid'])}},
            {'$set': {'data.room': new_room}, '$unset': {'data.room_exkey': 1}},
        )

        cls.update_room_key(pid=pid, uids=(uid, ex_mate['uid']))

        logging.info('已交換 %s %s %s', new_room, uid, ex_mate['uid'])

        old_mates = list(FormDB().find(
            {'case': 'accommodation', 'pid': pid,
             'data.room': {'$in': (data['data']['room'], ex_mate['data']['room'])}}))

        logging.info('old_mates: %s', ', '.join(
            [mate['uid'] for mate in old_mates]))

        if len(old_mates) < 2:
            return '交換完畢'

        uids = [mate['uid'] for mate in old_mates]
        user_infos = User.get_info(uids=uids, need_sensitive=True)
        if user_infos[uids[0]]['profile_real']['roc_id'][1] != user_infos[
                uids[1]]['profile_real']['roc_id'][1]:
            logging.info('old_mates 性別不同，不交換。')
            return '交換完畢'

        new_room = 'R-'+f'{uuid4().fields[0]:04x}'

        FormDB().update_many(
            {'case': 'accommodation', 'pid': pid, 'uid': {'$in': uids}},
            {'$set': {'data.room': new_room}, '$unset': {'data.room_exkey': 1}},
        )

        cls.update_room_key(pid=pid, uids=uids)

        logging.info('old_mates new rooms: %s, %s', new_room, ', '.join(uids))

        return '交換完畢'
