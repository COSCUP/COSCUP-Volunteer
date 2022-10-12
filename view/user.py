''' User '''
import html
import re
from urllib.parse import quote_plus

import arrow
from flask import Blueprint, redirect, render_template, url_for
from markdown import markdown

from module.gsuite import GSuite
from module.mattermost_bot import MattermostTools
from module.oauth import OAuth
from module.project import Project
from module.team import Team
from module.users import User

VIEW_USER = Blueprint('user', __name__, url_prefix='/user')


@VIEW_USER.route('/')
def index():
    ''' Index '''
    return 'user'


@VIEW_USER.route('/<uid>/<nickname>')
@VIEW_USER.route('/<uid>')
def user_page(uid, nickname=None):
    ''' User page '''
    user = User(uid=uid).get()

    if not user:
        return '', 200

    oauth = OAuth(user['mail']).get()

    if 'data' in oauth and 'picture' in oauth['data']:
        oauth['data']['picture'] = GSuite.size_picture(
            oauth['data']['picture'])

    if 'profile' in user and 'badge_name' in user['profile']:
        _nickname = user['profile']['badge_name']
    else:
        _nickname = oauth['data']['name']

    _nickname = quote_plus(_nickname)

    if nickname is None or nickname != _nickname:
        return redirect(url_for('user.user_page', uid=uid, nickname=_nickname))

    if 'profile' not in user:
        badge_name = ''
        intro = ''
    else:
        badge_name = user['profile']['badge_name']

        intro = ''
        if 'intro' in user['profile']:
            intro = re.sub('<a href="javascript:.*"', '<a href="/"',
                           markdown(html.escape(user['profile']['intro'])))

    participate_in = []
    for item in Team.participate_in(uid):
        project = Project.get(item['pid'])
        if not project:
            raise Exception('No project')

        item['_project'] = project.dict(by_alias=True)
        item['_title'] = '???'
        if uid in item['chiefs']:
            item['_title'] = 'chief'
        elif uid in item['members']:
            item['_title'] = 'member'

        item['_action_date'] = arrow.get(
            item['_project']['action_date']).format('YYYY/MM')

        participate_in.append(item)

    participate_in = sorted(
        participate_in, key=lambda p: p['_project']['action_date'], reverse=True)

    mattermost_data = {}
    mid = MattermostTools.find_possible_mid(uid=uid)
    if mid:
        mattermost_data['mid'] = mid
        mattermost_data['username'] = MattermostTools.find_user_name(mid=mid)

    return render_template('./user.html',
                           badge_name=badge_name,
                           intro=intro,
                           oauth=oauth,
                           user=user,
                           mattermost_data=mattermost_data,
                           participate_in=participate_in,
                           )
