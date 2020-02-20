import html

import arrow
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from markdown import markdown

from module.mattermost_link import MattermostLink
from module.oauth import OAuth
from module.project import Project
from module.team import Team
from module.users import User


VIEW_USER = Blueprint('user', __name__, url_prefix='/user')

@VIEW_USER.route('/')
def index():
    return u'user'

@VIEW_USER.route('/<uid>/<nickname>')
@VIEW_USER.route('/<uid>')
def user_page(uid, nickname=None):
    user = User(uid=uid).get()

    if not user:
        return u'', 200

    oauth = OAuth(user['mail']).get()

    if 'profile' in user and 'badge_name' in user['profile']:
        _nickname = user['profile']['badge_name'].replace(' ', '_')
    else:
        _nickname = oauth['data']['name'].replace(' ', '_')

    if nickname is None or nickname != _nickname:
        return redirect(url_for('user.user_page', uid=uid, nickname=_nickname))

    if 'profile' not in user:
        badge_name = ''
        intro = ''
    else:
        badge_name = user['profile']['badge_name']
        intro = markdown(html.escape(user['profile']['intro']))

    participate_in = []
    for p in Team.participate_in(uid):
        p['_project'] = Project.get(p['pid'])
        p['_title'] = '???'
        if uid in p['chiefs']:
            p['_title'] = 'chief'
        elif uid in p['members']:
            p['_title'] = 'member'

        p['_action_date'] = arrow.get(p['_project']['action_date']).format('YYYY/MM')

        participate_in.append(p)

    sorted(participate_in, key=lambda p: p['_project']['action_date'], reverse=True)


    return render_template('./user.html',
            badge_name=badge_name,
            intro=intro,
            oauth=oauth,
            user=user,
            mml=MattermostLink(uid=user['_id']),
            participate_in=participate_in,
    )
