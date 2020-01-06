import os
import hashlib
from urllib.parse import parse_qs
from urllib.parse import urlparse

import google_auth_oauthlib.flow
from apiclient import discovery
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for

import setting
from module.oauth import OAuth
from module.users import User

app = Flask(__name__)
app.secret_key = setting.secret_key

NO_NEED_LOGIN_PATH = (
    '/',
    '/oauth2callback',
    '/logout',
)

@app.before_request
def need_login():
    print('[X-SSL-SESSION-ID: %s] [SESSION: %s]' % (request.headers.get('X-SSL-SESSION-ID'), session))

    #if request.path not in NO_NEED_LOGIN_PATH:
    #    if not session.get('u') or session.get('u').get('email') not in setting.ALLOW_USER:
    #        session['r'] = request.path
    #        return redirect(url_for('oauth2logout'))

@app.route('/')
def index():
    return u'Hello'


@app.route('/oauth2callback')
def oauth2callback():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        './client_secret.json',
        scopes=(
          'openid',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
        ),
        redirect_uri='https://secretary.coscup.org/oauth2callback',
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

        auth_client = discovery.build('oauth2', 'v2', credentials=flow.credentials)
        user_info = auth_client.userinfo().get().execute()

        # ----- save oauth info ----- #
        OAuth.add(mail=user_info['email'], data=user_info, token=flow.credentials)

        # ----- Check account or create ----- #
        owner = OAuth.owner(mail=user_info['email'])
        if owner:
            user = User(uid=owner).get()
        else:
            user = User.create(mail=user_info['email'])

        return u'<pre>%s</pre><br>User:<pre>%s</pre>' % (user_info, user)

    return u'state fail', 400

@app.route('/logout')
def oauth2logout():
    ''' Logout

        **GET** ``/logout``

        :return: Remove cookie/session.
    '''
    session.pop('u', None)
    return redirect(url_for('index', _scheme='https', _external=True))

if __name__ == '__main__':
    app.run(debug=False, host=setting.SERVER_HOST, port=setting.SERVER_PORT)
