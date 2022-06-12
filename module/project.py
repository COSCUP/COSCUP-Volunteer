''' Project '''
from typing import Any, Optional

import arrow
from pymongo.cursor import Cursor

from models.projectdb import ProjectDB


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
        projectdb = ProjectDB(pid)

        data = projectdb.default()
        data['name'] = name
        data['owners'].extend(owners)
        data['action_date'] = arrow.get(action_date).timestamp()

        return projectdb.add(data)

    @staticmethod
    def all() -> Cursor[dict[str, Any]]:
        ''' List all project

        Returns:
            Return all projects and order by `action_date`(desc).

        '''
        return ProjectDB(pid='').find({}, sort=(('action_date', -1), ))

    @staticmethod
    def get(pid: str) -> Optional[dict[str, Any]]:
        ''' Get project info

        Args:
            pid (str): Project id.

        Returns:
            Return the project info.

        '''
        return ProjectDB(pid).find_one({'_id': pid})

    @staticmethod
    def update(pid: str, data: dict[str, Any]) -> None:
        ''' update data

        Args:
            pid (str): Project id.
            data (dict): The data to update. These fields can be updated:
                         `name`, `desc`, `volunteer_certificate_hours`, `calendar`,
                         `mailling_staff`, `mailling_leader`, `shared_drive`,
                         `mattermost_ch_id`, `traffic_fee_doc`, `gitlab_project_id`,
                         `parking_card`.

        '''
        _data = {}
        for k in ('name', 'desc', 'volunteer_certificate_hours', 'calendar',
                  'mailling_staff', 'mailling_leader', 'shared_drive', 'mattermost_ch_id',
                  'traffic_fee_doc', 'gitlab_project_id', 'parking_card'):
            if k in data:
                _data[k] = data[k]

                if isinstance(_data[k], str):
                    _data[k] = _data[k].strip()

        if 'volunteer_certificate_hours' in _data:
            _data['volunteer_certificate_hours'] = int(
                _data['volunteer_certificate_hours'])

        ProjectDB(pid).find_one_and_update({'_id': pid}, {'$set': _data})
