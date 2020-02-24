import logging
logging.basicConfig(
    filename='./log/log.log',
    format='%(asctime)s [%(levelname)-5.5s][%(thread)6.6s] [%(module)s:%(funcName)s#%(lineno)d]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)

import hashlib
import os
import traceback
#import re
from urllib.parse import parse_qs
from urllib.parse import urlparse

import arrow
import google_auth_oauthlib.flow
from apiclient import discovery
from flask import Flask
from flask import g
from flask import got_request_exception
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import setting
from celery_task.task_mail_sys import mail_sys_weberror
from models.mailletterdb import MailLetterDB
from module.oauth import OAuth
from module.users import User
from module.usession import USession
from view.guide import VIEW_GUIDE
from view.links import VIEW_LINKS
from view.project import VIEW_PROJECT
from view.setting import VIEW_SETTING
from view.team import VIEW_TEAM
from view.user import VIEW_USER


app = Flask(__name__)
app.config['SESSION_COOKIE_SECURE'] = True
app.secret_key = setting.SECRET_KEY
app.register_blueprint(VIEW_GUIDE)
app.register_blueprint(VIEW_LINKS)
app.register_blueprint(VIEW_PROJECT)
app.register_blueprint(VIEW_SETTING)
app.register_blueprint(VIEW_TEAM)
app.register_blueprint(VIEW_USER)


NO_NEED_LOGIN_PATH = (
    '/',
    '/oauth2callback',
    '/logout',
    '/links/chat',
    '/privacy',
    '/bug-report',
)


@app.before_request
def need_login():
    app.logger.info('[X-SSL-SESSION-ID: %s] [X-REAL-IP: %s] [USER-AGENT: %s] [SESSION: %s]' % (
            request.headers.get('X-SSL-SESSION-ID'),
            request.headers.get('X-REAL-IP'),
            request.headers.get('USER-AGENT'),
            session, )
       )

    if request.path.startswith('/user') and request.path[-1] == '/':
        return redirect(request.path[:-1])

    if 'sid' in session and session['sid']:
        session_data = USession.get(session['sid'])
        if session_data:
            uid = session_data['uid']

            g.user = {}
            g.user['account'] = User(uid=session_data['uid']).get()

            if g.user['account']:
                g.user['data'] = OAuth(mail=g.user['account']['mail']).get()['data']
            else:
                session.pop('sid', None)
    else:
        if request.path not in NO_NEED_LOGIN_PATH:
            # ----- Let user profile public ----- #
            #if re.match(r'(\/user\/[a-z0-9]{8}).*', request.path):
            #    return

            session['r'] = request.path
            return redirect(url_for('oauth2callback', _scheme='https', _external=True))


@app.route('/')
def index():
    if 'user' in g:
        return render_template('index_guide.html')

    return render_template('index.html')


@app.route('/oauth2callback')
def oauth2callback():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        './client_secret.json',
        scopes=(
          'openid',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
        ),
        redirect_uri='https://%s/oauth2callback' % setting.DOMAIN,
    )

    if 'code' not in request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=hashlib.sha256(os.urandom(2048)).hexdigest(),
        )

        session['state'] = state
        return redirect(authorization_url)

    url = request.url.replace('http://', 'https://')
    url_query = parse_qs(urlparse(url).query)

    if 'state' in url_query and url_query['state'] and url_query['state'][0] == session.get('state'):
        flow.fetch_token(authorization_response=url)

        auth_client = discovery.build('oauth2', 'v2', credentials=flow.credentials, cache_discovery=False)
        user_info = auth_client.userinfo().get().execute()

        # ----- save oauth info ----- #
        OAuth.add(mail=user_info['email'], data=user_info, token=flow.credentials)

        # ----- Check account or create ----- #
        owner = OAuth.owner(mail=user_info['email'])
        if owner:
            user = User(uid=owner).get()
        else:
            user = User.create(mail=user_info['email'])
            MailLetterDB().create(uid=user['_id'])

        user_session= USession.make_new(uid=user['_id'], header=dict(request.headers))
        session['sid'] = user_session.inserted_id

        if 'r' in session:
            r = session['r']
            session.pop('r', None)
            return redirect(r)

        return redirect(url_for('index', _scheme='https', _external=True))

    else:
        session.pop('state', None)
        return redirect(url_for('oauth2callback', _scheme='https', _external=True))


@app.route('/logout')
def oauth2logout():
    ''' Logout

        **GET** ``/logout``

        :return: Remove cookie/session.
    '''
    session.pop('state', None)
    session.pop('sid', None)
    return redirect(url_for('index', _scheme='https', _external=True))

@app.route('/privacy')
def privacy():
    return render_template('./privacy.html', content=setting.PRIVACY_CONTENT)

@app.route('/bug-report')
def bug_report():
    return render_template('./bug_report.html')

@app.route('/exception')
def exception():
    try:
        1/0
    except Exception as e:
        raise Exception('Error: [%s]' % e)


def error_exception(sender, exception, **extra):
    mail_sys_weberror.apply_async(
        kwargs={
            'title': u'%s %s %s' % (request.method, request.path, arrow.now()),
            'body': '''<b>%s</b> %s<br>
            <pre>%s</pre>
            <pre>%s</pre>
            <pre>User: %s\n\nsid: %s\n\nargs: %s\n\nform: %s\n\nvalues: %s\n\n%s</pre>''' %
            (request.method, request.path, os.environ, request.headers,
             g.get('user', {}).get('account', {}).get('_id'), session.get('sid'), request.args, request.form, request.values, traceback.format_exc())
        })

got_request_exception.connect(error_exception, app)


if __name__ == '__main__':
    app.run(debug=False, host=setting.SERVER_HOST, port=setting.SERVER_PORT)
