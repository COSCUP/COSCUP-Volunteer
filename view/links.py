from flask import Blueprint
from flask import request

from module.mattermost_link import MattermostLink

VIEW_LINKS = Blueprint('links', __name__, url_prefix='/links')


@VIEW_LINKS.route('/')
def index():
    return u'hi'


@VIEW_LINKS.route('/chat', methods=('POST', ))
def link_chat():
    if request.method == 'POST':
        if MattermostLink.verify_save(request.form):
            return u'認證成功 / Completed'

        return u'認證失敗 / Fail'
