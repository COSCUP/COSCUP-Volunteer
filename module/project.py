''' Project '''
from typing import Any, Generator

from models.projectdb import ProjectDB
from structs.projects import ProjectBase


class Project:
    ''' Project module '''
    @staticmethod
    def create(pid: str, name: str, owners: list[str], action_date: str) -> dict[str, Any]:
        ''' Create project

        Args:
            pid (str): Project id.
            name (str): Project name.
            owners (list): List of owner's uids.
            action_date: The date at the event first date.

        Returns:
            Return the added data.

        '''
        new_project = ProjectBase.parse_obj({
            '_id': pid, 'name': name, 'owners': owners, 'action_date': action_date,
        })

        return ProjectDB(pid=pid).add(data=new_project.dict(by_alias=True))

    @staticmethod
    def all() -> Generator[ProjectBase, None, None]:
        ''' List all project

        Returns:
            Return all projects and order by `action_date`(desc).

        '''
        for item in ProjectDB(pid='').find({}, sort=(('action_date', -1), )):
            yield ProjectBase.parse_obj(item)

    @staticmethod
    def get(pid: str) -> ProjectBase | None:
        ''' Get project info

        Args:
            pid (str): Project id.

        Returns:
            Return the project info.

        '''
        for item in ProjectDB(pid).find({'_id': pid}):
            return ProjectBase.parse_obj(item)

        return None

    @staticmethod
    def update(pid: str, data: dict[str, Any]) -> None:
        ''' update data

        Args:
            pid (str): Project id.
            data (dict): The data to update. These fields can be updated:
                         `name`, `desc`, `volunteer_certificate_hours`, `calendar`,
                         `mailling_staff`, `mailling_leader`, `shared_drive`,
                         `mattermost_ch_id`, `traffic_fee_doc`, `gitlab_project_id`,
                         `parking_card`, `action_date`.

        '''
        _data = {}
        for k in ('name', 'desc', 'volunteer_certificate_hours', 'calendar',
                  'mailling_staff', 'mailling_leader', 'shared_drive', 'mattermost_ch_id',
                  'traffic_fee_doc', 'gitlab_project_id', 'parking_card', 'action_date'):
            if k in data:
                _data[k] = data[k]

                if isinstance(_data[k], str):
                    _data[k] = _data[k].strip()

        if 'volunteer_certificate_hours' in _data:
            _data['volunteer_certificate_hours'] = int(
                _data['volunteer_certificate_hours'])

        if 'action_date' in _data:
            _data['action_date'] = int(_data['action_date'])

        ProjectDB(pid).find_one_and_update({'_id': pid}, {'$set': _data})
