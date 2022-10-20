''' utils '''
from flask import redirect
from werkzeug.wrappers import Response as ResponseBase

from module.project import Project
from module.team import Team
from structs.projects import ProjectBase
from structs.teams import TeamBase


def check_the_team_and_project_are_existed(pid: str, tid: str) -> \
        tuple[TeamBase, ProjectBase, None] | tuple[None, None, ResponseBase]:
    ''' Base check the team and profect are existed

    :param str pid: project id
    :param str tid: team id
    :rtype: tuple
    :return: team, project, redirect

    '''
    team = Team.get(pid, tid)
    if not team:
        return None, None, redirect('/')

    project = Project.get(pid)
    if not project:
        return None, None, redirect('/')

    return team, project, None
