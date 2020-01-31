from models.formdb import FormDB


class Form(object):
    ''' Form Object '''
    TRAFFIC_FEE_LOCATIONS = (
        ('基隆', 114),
        ('大台北地區', 110),
        ('宜蘭', 380),
        ('桃園', 162),
        ('新竹', 320),
        ('苗栗', 420),
        ('臺中', 640),
        ('彰化', 690),
        ('南投', 790),
        ('雲林', 850),
        ('嘉義', 870),
        ('臺南', 930),
        ('高雄', 1120),
        ('屏東', 1200),
        ('花蓮', 880),
        ('臺東', 1566),
        ('離島', 1200),
    )

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
