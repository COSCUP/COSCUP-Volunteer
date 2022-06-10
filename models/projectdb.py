''' ProjectDB '''
from typing import Any

from pymongo.collection import ReturnDocument

from models.base import DBBase


class ProjectDB(DBBase):
    ''' Project Collection

    Args:
        pid (str): Project id.

    Attributes:
        pid (str): Project id.

    Struct:
        - ``_id``: Project id (pid)
        - ``name``: Project name for display.
        - ``action_date``: `timestamp` The first date of the event launched.
        - ``created_at``: `timestamp` The data created at.
        - ``desc``: Description.
        - ``owners``: List of uid. The permissions of `owner` has the top level over the project.
        - ``calendar``: Google Calendar id. The ID patten should be
                        `{a-z0-9_}@group.calendar.google.com`.
        - ``gitlab_project_id``: Gitlab project id.
        - ``mailling_leader``: The mailing-list for team leaders.
        - ``mailling_staff``: The mailing-list for all project staffs.
        - ``mattermost_ch_id``: The chat room for Mattermost.
        - ``shared_drive``: Google Shared Drive URL.
        - ``traffic_fee_doc``: The announcement URL of the traffic subsidy document.
        - ``volunteer_certificate_hours``: The hours for volunteers to apply for.
        - ``parking_card``: The options for parking card in form.

    TODO:
        Need refactor in pydantic.

    '''

    def __init__(self, pid: str) -> None:
        super().__init__('project')
        self.pid = pid

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `owners`, `action_date`

        '''
        self.create_index([('owners', 1), ('action_date', -1)])

    def default(self) -> dict[str, Any]:
        ''' default data

        Returns:
            The default data will only return the required fields in `_id`, `name`,
                `action_date`, `desc`, `owners`.

        '''
        result = {
            '_id': self.pid,
            'name': '',
            'action_date': 0,
            'desc': '',
            'owners': [],
        }
        self.make_create_at(result)
        return result

    def add(self, data: dict[str, Any]) -> dict[str, Any]:
        ''' Add data

        Args:
            data (dict): The data to inserted / updated.

        Returns:
            Return the inserted / updated data.

        '''
        return self.find_one_and_update(
            {'_id': data['_id']},
            {'$set': data},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
