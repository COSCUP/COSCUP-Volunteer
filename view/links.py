''' Links '''
from flask import Blueprint, request
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

from module.mattermost_link import MattermostLink

VIEW_LINKS = Blueprint('links', __name__, url_prefix='/links')


@VIEW_LINKS.route('/')
def index() -> str:
    ''' Index page '''
    return 'hi'


@VIEW_LINKS.route('/chat', methods=('POST', ))
def link_chat() -> ResponseBase:
    ''' Link to chat '''
    if request.method == 'POST':
        if MattermostLink.verify_save(request.form):
            return Response('認證成功 / Completed')

        return Response('認證失敗 / Fail')

    return Response('', status=404)
