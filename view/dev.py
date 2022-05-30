from typing import Text

from flask import (Blueprint, Response, g, jsonify, redirect, render_template,
                   request, session, url_for)

VIEW_DEV = Blueprint('dev', __name__, url_prefix='/dev')


@VIEW_DEV.route('/')
def index() -> Text:
    ''' Index page '''
    if 'tc' not in session:
        session['tc'] = 0

    session['tc'] += 1

    return f"Hi developer! [{session['tc']}]"


@VIEW_DEV.route('/cookie')
def set_cookie() -> Text:
    ''' set cookies '''
    session['sid'] = request.args['sid']
    return f"sid: {request.args['sid']}"
