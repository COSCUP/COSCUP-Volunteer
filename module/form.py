from models.formdb import FormDB


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
