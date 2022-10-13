''' Project '''
from typing import Any, Generator

from pymongo.collection import ReturnDocument

from models.projectdb import ProjectDB
from structs.projects import ProjectBase, ProjectBaseUpdate


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

        return ProjectDB(pid=pid).add(
            data=new_project.dict(by_alias=True, exclude_none=True))

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
    def update(pid: str, data: ProjectBaseUpdate) -> ProjectBaseUpdate:
        ''' update data

        Args:
            pid (str): Project id.
            data (dict): The data to update.
                         Can be updated fields refer to [structs.projects.ProjectBaseUpdate][]

        '''
        _data = data.dict(exclude_none=True)
        result = ProjectDB(pid).find_one_and_update(
            {'_id': pid},
            {'$set': _data},
            return_document=ReturnDocument.AFTER,
        )

        return ProjectBaseUpdate.parse_obj(result)
