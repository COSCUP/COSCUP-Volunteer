from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for

from module.oauth import OAuth
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
        return u'.', 404

    oauth = OAuth(user['mail']).get()

    _nickname = oauth['data']['name'].replace(' ', '_')

    if nickname is None or nickname != _nickname:
        return redirect(url_for('user.user_page', uid=uid, nickname=_nickname))

    return u'%s, %s' % (user['_id'], nickname)
