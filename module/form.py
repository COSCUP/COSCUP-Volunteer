from models.formdb import FormDB
from models.formdb import FormTrafficFeeMappingDB


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
