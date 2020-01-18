from flask import Blueprint
from flask import render_template

from module.project import Project
from module.team import Team

VIEW_TEAM = Blueprint('team', __name__, url_prefix='/team')


@VIEW_TEAM.route('/<pid>/<tid>/')
def index(pid, tid):
    team = Team.get(pid, tid)

    return render_template('./team.html', team=team)
