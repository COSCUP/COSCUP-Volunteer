''' Links '''
from flask import Blueprint, request

from module.mattermost_link import MattermostLink

VIEW_LINKS = Blueprint('links', __name__, url_prefix='/links')


@VIEW_LINKS.route('/')
def index():
    ''' Index page '''
    return 'hi'


@VIEW_LINKS.route('/chat', methods=('POST', ))
def link_chat():
    ''' Link to chat '''
    if request.method == 'POST':
        if MattermostLink.verify_save(request.form):
            return '認證成功 / Completed'

        return '認證失敗 / Fail'

    return '', 404
