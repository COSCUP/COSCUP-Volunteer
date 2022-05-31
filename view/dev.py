from typing import Text

from flask import (Blueprint, Response, g, jsonify, redirect, render_template,
                   request, session, url_for)

from models.users_db import UsersDB
from models.usessiondb import USessionDB

VIEW_DEV = Blueprint('dev', __name__, url_prefix='/dev')


@VIEW_DEV.route('/', methods=('GET', 'POST'))
def index() -> Text:
    ''' Index page '''
    if request.method == 'GET':
        if 'tc' not in session:
            session['tc'] = 0

        session['tc'] += 1

        return render_template('./dev_index.html', count=session['tc'])

    if request.method == 'POST':
        data = request.get_json()

        if data:
            if 'casename' in data and data['casename'] == 'get':
                accounts = []
                sessions = []
                for user in UsersDB().find():
                    accounts.append(user)

                for usession in USessionDB().find():
                    sessions.append(usession)

                return jsonify({
                    'sid': session['sid'],
                    'accounts': accounts,
                    'sessions': sessions,
                })

    return jsonify({})


@VIEW_DEV.route('/cookie')
def set_cookie() -> Text:
    ''' set cookies '''
    session['sid'] = request.args['sid']
    return redirect(url_for('dev.index'))
