''' Form '''
import logging
from collections.abc import Iterable
from typing import Any, Generator, Optional
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.formdb import FormDB, FormTrafficFeeMappingDB
from module.users import User
from structs.projects import ProjectTrafficLocationFeeItem


class Form:  # pylint: disable=too-many-public-methods
    ''' Form Object '''
    @staticmethod
    def update_appreciation(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update appreciation

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `available`: `bool`.
                - `key`: In one of `oauth`, `badge_name`, `real_name`.
                - `value`: As user name.

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='appreciation', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_appreciation(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get appreciation

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'appreciation', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_appreciation(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all appreciation

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'appreciation', 'pid': pid}):
            yield raw

    @staticmethod
    def update_volunteer_certificate(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update volunteer certificate

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `value`: `bool`.

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='volunteer_certificate', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_volunteer_certificate(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get volunteer certificate

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'volunteer_certificate', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_volunteer_certificate(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get All volunteer certificate

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'volunteer_certificate', 'pid': pid}):
            yield raw

    @staticmethod
    def update_traffic_fee(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update traffic fee

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `apply`: `bool`.
                - `fee`: `int`.
                - `fromwhere`: `str`.
                - `howto`: `str`.

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='traffic_fee', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_traffic_fee(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get traffic fee

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'traffic_fee', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_traffic_fee(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get All traffic_fee

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'traffic_fee', 'pid': pid}):
            yield raw

    @staticmethod
    def update_accommodation(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update accommodation

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `key`: In one of `yes-longtraffic`, `yes`, `no`.
                - `status`: `bool`.
                - `room`: Optional. The room numbers.
                - `room_key`: Optional. The key for exchange the place for
                              some users want live together.
                - `mixed`: (bool) accepted in mixed room.

        Returns:
            Return the added data.

        See Also:
            The more about how to use the `room_key` to exchange the `room`,
                please move to [module.form.FormAccommodation][].

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='accommodation', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_accommodation(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get accommodation

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'accommodation', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_accommodation(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all accommodation

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'accommodation', 'pid': pid}):
            yield raw

    @staticmethod
    def update_clothes(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update clothes

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `clothes`: `S / 38.5 / 55` ...

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='clothes', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_clothes(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get clothes

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'clothes', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_clothes(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all clothes

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'clothes', 'pid': pid}):
            yield raw

    @staticmethod
    def update_parking_card(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update parking card

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `carno`: The license plate.
                - `dates`: List of dates. The dates options are from
                           the collection of `db.project.parking_card`.

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='parking_card', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_parking_card(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get parking card

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'parking_card', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_parking_card(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all parking card

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'parking_card', 'pid': pid}):
            yield raw

    @staticmethod
    def update_drink(pid: str, uid: str, data: dict[str, Any]) -> dict[str, Any]:
        ''' Update drink

        Args:
            pid (str): Project id.
            uid (str): User id.
            data (dict): The data to update.

                - `y18`: `bool`.

        Returns:
            Return the added data.

        TODO:
            Need refactor in pydantic.

        '''
        return FormDB().add_by_case(case='drink', pid=pid, uid=uid, data=data)

    @staticmethod
    def get_drink(pid: str, uid: str) -> Optional[dict[str, Any]]:
        ''' Get drink

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            The data or `None`.

        '''
        return FormDB().find_one({'case': 'drink', 'pid': pid, 'uid': uid})

    @staticmethod
    def all_drink(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get all drink

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'drink', 'pid': pid}):
            yield raw


class FormTrafficFeeMapping:
    ''' FormTrafficFeeMapping object '''

    @staticmethod
    def save(pid: str, datas: list[ProjectTrafficLocationFeeItem]) -> list[
            ProjectTrafficLocationFeeItem]:
        ''' Save mapping data

        :param str pid: pid
        :param dict data: location/fee mapping

        Args:
            pid (str): Project id.
            datas (list): location/fee mapping datas.

        Returns:
            Return the saved data.

        '''
        _data = {}
        for item in datas:
            _data[item.location] = item.fee

        result = []
        saved = FormTrafficFeeMappingDB().save(pid=pid, data=_data)
        for location, fee in saved['data'].items():
            result.append(ProjectTrafficLocationFeeItem.parse_obj({
                'location': location, 'fee': fee}))

        return result

    @staticmethod
    def get(pid: str) -> list[ProjectTrafficLocationFeeItem]:
        ''' Get

        :param str pid: pid

        Args:
            pid (str): Project id.

        Returns:
            The data or `None`.

        '''
        result = []
        datas = FormTrafficFeeMappingDB().find_one({'_id': pid})
        if datas and 'data' in datas:
            for location, fee in datas['data'].items():
                result.append(ProjectTrafficLocationFeeItem.parse_obj({
                    'location': location,
                    'fee': fee,
                }))
        return result


class FormAccommodation:
    ''' FormAccommodation object '''
    @staticmethod
    def get(pid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get data, and in `yes-longtraffic`, `yes`.

        Args:
            pid (str): Project id.

        Yields:
            Return the data in `pid`.

        '''
        for raw in FormDB().find({'case': 'accommodation', 'pid': pid, 'data.key': {'$ne': 'no'}}):
            yield raw

    @staticmethod
    def update_room(pid: str, uid: str, room: str, change_key: bool = True) -> dict[str, Any]:
        ''' Update room no

        Update will happend in `room`

        - Not the same with `room`.
        - Not yet have the `room`.

        Args:
            pid (str): Project id.
            uid (str): User id.
            room (str): Room numbers.
            change_key (bool): To generate a new `room_key`.

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
        ''' update / regenerate the room key

        Args:
            pid (str): Project id.
            uids (list): User ids.

        '''
        for uid in uids:
            FormDB().find_one_and_update(
                {'case': 'accommodation', 'pid': pid, 'uid': uid}, {
                    '$set': {'data.room_key': f'{uuid4().fields[0]:08x}'}},
            )

    @staticmethod
    def get_room_mate(pid: str, uid: str) -> \
            tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        ''' Get room mate

        Args:
            pid (str): Project id.
            uid (str): User id.

        Returns:
            (`user_room`, `mate`)

                - `user_room`: User's room info.
                - `mate`: User's room mate info.

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

        Args:
            pid (str): Project id.
            uid (str): User id.
            exkey (str): Exchange key.

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
