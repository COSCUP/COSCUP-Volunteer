import arrow

from models.projectdb import ProjectDB


class Project(object):
    ''' Project module '''
    @staticmethod
    def create(pid, name, owners, action_date):
        ''' Create project

        :param str pid: project id
        :param str name: project name
        :param list owners: str of list
        :param str action_date: date format

        '''
        projectdb = ProjectDB(pid)

        data = projectdb.default()
        data['name'] = name
        data['owners'].extend(owners)
        data['action_date'] = arrow.get(action_date).timestamp

        return projectdb.add(data)

    @staticmethod
    def all():
        ''' List all project '''
        return ProjectDB(pid=None).find()

    @staticmethod
    def get(pid):
        ''' Get project info

        :param str pid: project id

        '''
        return ProjectDB(pid).find_one({'_id': pid})

    @staticmethod
    def update(pid, data):
        ''' update data

        :param dict data: data

        '''
        _data = {}
        for k in ('name', 'desc', 'volunteer_certificate_hours', 'calendar', 'mailling_staff', 'mailling_leader'):
            if k in data:
                _data[k] = data[k]

                if isinstance(_data[k], str):
                    _data[k] = _data[k].strip()

        if 'volunteer_certificate_hours' in _data:
            _data['volunteer_certificate_hours'] = int(_data['volunteer_certificate_hours'])

        ProjectDB(pid).find_one_and_update({'_id': pid}, {'$set': _data})
