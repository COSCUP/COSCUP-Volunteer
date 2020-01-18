import math

import arrow
from flask import Blueprint
from flask import render_template

from module.project import Project
from module.team import Team

VIEW_PROJECT = Blueprint('project', __name__, url_prefix='/project')


@VIEW_PROJECT.route('/')
def index():
    projects = []
    data = list(Project.all())
    for d in data:
        date = arrow.get(d['action_date'])
        d['action_date_str'] = '%s (%s)' % (date.format('YYYY-MM-DD'), date.humanize(arrow.now()))

    per = 3
    for i in range(int(math.ceil(len(data) / float(per)))):
        projects.append(data[per*i:min([per*(i+1), len(data)])])

    return render_template('./project_index.html', projects=projects)

@VIEW_PROJECT.route('/<pid>/')
def team_page(pid):
    teams = []
    project = Project.get(pid)
    if not project:
        return u'no data', 404

    data = list(Team.list_by_pid(project['_id']))

    per = 3
    for i in range(int(math.ceil(len(data) / float(per)))):
        teams.append(data[per*i:min([per*(i+1), len(data)])])

    return render_template('./project_teams_index.html', teams=teams, project=project)
