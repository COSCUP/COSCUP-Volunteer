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
