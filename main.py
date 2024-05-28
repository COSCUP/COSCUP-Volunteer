''' main '''
# pylint: disable=no-member
import logging
import os
import re
import secrets
import traceback
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, quote_plus, urlparse

import arrow
import google_auth_oauthlib.flow
from apiclient import discovery
from flask import (Flask, flash, g, got_request_exception, make_response,
                   redirect, render_template, request, session, url_for)
from flask.wrappers import Response
from markdown import markdown
from werkzeug.wrappers import Response as ResponseBase

import setting
from celery_task.task_mail_sys import mail_sys_weberror
from models.mailletterdb import MailLetterDB
from module.mattermost_bot import MattermostTools
from module.mc import MC
from module.oauth import OAuth
from module.tasks import Tasks
from module.team import Team
from module.track import TalkFavs, Track
from module.users import PolicySigned, User
from module.usession import USession
from structs.users import PolicyType
from view.api import VIEW_API
from view.budget import VIEW_BUDGET
from view.dispense import VIEW_DISPENSE
from view.expense import VIEW_EXPENSE
from view.guide import VIEW_GUIDE
from view.links import VIEW_LINKS
from view.project import VIEW_PROJECT
from view.recruit import VIEW_RECRUIT
from view.schedule import VIEW_SCHEDULE
from view.sender import VIEW_SENDER
from view.setting import VIEW_SETTING
from view.tasks import VIEW_TASKS
from view.team import VIEW_TEAM
from view.telegram import VIEW_TELEGRAM
from view.user import VIEW_USER

logging.basicConfig(
    filename='/var/log/apps/log.log',
    format='%(asctime)s [%(levelname)-5.5s][%(thread)6.6s] [%(module)s:%(funcName)s#%(lineno)d]: %(message)s',  # pylint: disable=line-too-long
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = '__Host-vl'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True
app.secret_key = setting.SECRET_KEY
app.register_blueprint(VIEW_API)
app.register_blueprint(VIEW_BUDGET)
app.register_blueprint(VIEW_DISPENSE)
app.register_blueprint(VIEW_EXPENSE)
app.register_blueprint(VIEW_GUIDE)
app.register_blueprint(VIEW_LINKS)
app.register_blueprint(VIEW_PROJECT)
app.register_blueprint(VIEW_RECRUIT)
app.register_blueprint(VIEW_SCHEDULE)
app.register_blueprint(VIEW_SENDER)
app.register_blueprint(VIEW_SETTING)
app.register_blueprint(VIEW_TASKS)
app.register_blueprint(VIEW_TEAM)
app.register_blueprint(VIEW_TELEGRAM)
app.register_blueprint(VIEW_USER)
app.jinja_env.filters['quote_plus'] = quote_plus

# Enable TEMPLATES_AUTO_RELOAD with Debug mode enabled
if app.debug:
    app.config['TEMPLATES_AUTO_RELOAD'] = True

NO_NEED_LOGIN_PATH = {
    '/',
    '/oauth2callback',
    '/logout',
    '/links/chat',
    '/privacy',
    '/coc',
    '/security_guard',
    '/bug-report',
    '/robots.txt',
    '/api/members',
    '/telegram/r',
    '/sitemap.txt',
}


# For development mode.
# if `./view/dev.py` is exist, Append the `/dev` path into.
if Path('/app/view/dev.py').exists():
    logging.info('view.dev exists')
    from view.dev import VIEW_DEV
    app.register_blueprint(VIEW_DEV)
    NO_NEED_LOGIN_PATH.add('/dev/')
    NO_NEED_LOGIN_PATH.add('/dev/cookie')


@app.before_request
def need_login() -> ResponseBase | None:
    ''' need_login '''
    # pylint: disable=too-many-return-statements,too-many-branches
    logging.info('[X-SSL-SESSION-ID: %s] [X-REAL-IP: %s] [USER-AGENT: %s] [SESSION: %s]',
                 request.headers.get('X-SSL-SESSION-ID'),
                 request.headers.get('X-REAL-IP'),
                 request.headers.get('USER-AGENT'),
                 session, )

    if request.path.startswith('/user') and request.path[-1] == '/':
        for uid in re.finditer('[a-z0-9]{8}', request.path):
            return redirect(f'/user/{uid.group()}')

    if 'sid' in session and session['sid']:
        mem_cahce = MC.get_client()
        user_g_data = mem_cahce.get(f"sid:{session['sid']}")

        if user_g_data:
            g.user = user_g_data  # pylint: disable=assigning-non-slot
        else:
            session_data = USession.get(session['sid'])
            if session_data:
                has_suspended: bool | None = mem_cahce.get(
                    f"suspend:{session_data['uid']}")
                if has_suspended is None:
                    has_suspended = User(session_data['uid']).has_suspended()

                    if has_suspended:
                        mem_cahce.set(
                            f"suspend:{session_data['uid']}", True, 300)
                    else:
                        mem_cahce.set(
                            f"suspend:{session_data['uid']}", False, 300)

                if has_suspended:
                    session.pop('sid', None)
                    return redirect('/docs/zh-TW/error_note/e001/')

                g.user = {}  # pylint: disable=assigning-non-slot
                g.user['account'] = User(uid=session_data['uid']).get()

                if g.user['account']:
                    oauth = OAuth(
                        mail=g.user['account']['mail']).get()

                    if not oauth:
                        return None

                    call_func_pid: Callable[[
                        dict[str, Any], ], Any] = lambda x: x['pid']
                    g.user['data'] = oauth['data']
                    g.user['participate_in'] = sorted([
                        {'pid': team['pid'], 'tid': team['tid'],
                            'name': team['name']}
                        for team in Team.participate_in(
                            uid=session_data['uid'])], key=call_func_pid, reverse=True)

                    mem_cahce.set(f"sid:{session['sid']}", g.user, 600)
            else:
                session.pop('sid', None)
                session['r'] = request.path

                return redirect(url_for('oauth2callback', _scheme='https', _external=True))

        return None

    if request.path in NO_NEED_LOGIN_PATH or \
            request.path.startswith('/static/') or \
            request.path.startswith('/tasks') or \
    request.path.startswith('/schedule'):
        return None

    if request.path not in NO_NEED_LOGIN_PATH:
        # ----- Let user profile public ----- #
        # if re.match(r'(\/user\/[a-z0-9]{8}).*', request.path):
        #    return

        session['r'] = request.path
        logging.info('r: %s', session['r'])
        return redirect(url_for('oauth2callback', _scheme='https', _external=True))

    session.pop('sid', None)
    session['r'] = request.path

    return redirect(url_for('oauth2callback', _scheme='https', _external=True))


@app.after_request
def no_store(response: Response) -> Response:
    ''' return no-store '''
    if 'sid' in session and session['sid']:
        response.headers['Cache-Control'] = 'no-store'

    return response


@app.route('/')
def index() -> str:
    ''' index '''
    if 'user' not in g:
        return render_template('index.html')

    check = {
        'profile': False,
        'participate_in': False,
        'mattermost': False,
    }

    if 'profile' in g.user['account'] and 'intro' in g.user['account']['profile']:
        if len(g.user['account']['profile']['intro']) > 100:
            check['profile'] = True

    if list(Team.participate_in(uid=g.user['account']['_id'])):
        check['participate_in'] = True

    if MattermostTools.find_possible_mid(uid=g.user['account']['_id']):
        check['mattermost'] = True

    return render_template('index_guide.html', check=check)


@app.route('/oauth2callback')
def oauth2callback() -> ResponseBase:
    ''' oauth2callback '''
    if 'r' in request.args and request.args['r'].startswith('/'):
        session['r'] = request.args['r']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        './client_secret.json',
        scopes=(
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ),
        redirect_uri=f'https://{setting.DOMAIN}/oauth2callback',
    )

    if 'code' not in request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=secrets.token_urlsafe(64),
        )

        session['state'] = state
        return redirect(authorization_url)

    url = request.url.replace('http://', 'https://')
    url_query = parse_qs(urlparse(url).query)

    if 'state' in url_query and url_query['state'] and \
            url_query['state'][0] == session.get('state'):
        flow.fetch_token(authorization_response=url)

        auth_client = discovery.build(
            'oauth2', 'v2', credentials=flow.credentials, cache_discovery=False)
        user_info = auth_client.userinfo().get().execute()

        # ----- save oauth info ----- #
        OAuth.add(mail=user_info['email'],
                  data=user_info, token=flow.credentials)

        # ----- Check account or create ----- #
        owner = OAuth.owner(mail=user_info['email'])
        if owner:
            user = User(uid=owner).get()
        else:
            user = User.create(mail=user_info['email'])
            MailLetterDB().create(uid=user['_id'])

        if not user:
            return redirect(url_for('index', _scheme='https', _external=True))

        user_session = USession.make_new(
            uid=user['_id'], header=dict(request.headers))
        session['sid'] = user_session.inserted_id

        if 'r' in session:
            redirect_path = session['r']
            logging.info('login r: %s', redirect_path)
            session.pop('r', None)
            session.pop('state', None)
            return redirect(redirect_path)

        return redirect(url_for('index', _scheme='https', _external=True))

    session.pop('state', None)
    return redirect(url_for('oauth2callback', _scheme='https', _external=True))


@app.route('/logout')
def oauth2logout() -> ResponseBase:
    ''' Logout

        **GET** ``/logout``

        :return: Remove cookie/session.
    '''
    if 'sid' in session:
        USession.make_dead(sid=session['sid'])

    session.pop('state', None)
    session.pop('sid', None)
    return redirect(url_for('index', _scheme='https', _external=True))


@app.route('/privacy')
def privacy() -> str:
    ''' privacy '''
    mem_cahce = MC.get_client()
    content = mem_cahce.get('page:privacy')
    if not content:
        with open('./templates/privacy.md', 'r', encoding='UTF-8') as files:
            content = markdown(files.read())
            mem_cahce.set('page:privacy', content, 3600)

    return render_template('./privacy.html', content=content)


@app.route('/coc', methods=('GET', 'POST'))
def coc() -> ResponseBase | str:
    ''' coc '''
    if request.method == 'GET':
        mem_cahce = MC.get_client()
        content = mem_cahce.get('page:coc')
        if not content:
            with open('./templates/coc.md', 'r', encoding='UTF-8') as files:
                content = markdown(files.read())
                mem_cahce.set('page:coc', content, 3600)

        return render_template('./coc.html', content=content)

    if request.method == 'POST':
        if not g.user:
            return make_response({}, 404)

        PolicySigned.sign(
            uid=g.user['account']['_id'], _type=PolicyType.COC)

        flash('已簽署完成！')

    return redirect('/coc')


@app.route('/security_guard', methods=('GET', 'POST'))
def security_guard() -> ResponseBase | str:
    ''' Security Guard '''
    if request.method == 'GET':
        mem_cahce = MC.get_client()
        content = mem_cahce.get('page:security_g')
        if not content:
            with open('./templates/security_guard.md', 'r', encoding='UTF-8') as files:
                content = markdown(files.read())
                mem_cahce.set('page:security_g', content, 3600)

        return render_template('./security_guard.html', content=content)

    if request.method == 'POST':
        if not g.user:
            return make_response({}, 404)

        PolicySigned.sign(
            uid=g.user['account']['_id'], _type=PolicyType.SECURITY_GUARD)

        flash('已簽署完成！')

    return redirect('/security_guard')


@app.route('/bug-report')
def bug_report() -> str:
    ''' bug_report '''
    return render_template('./bug_report.html')


@app.route('/robots.txt')
def robots() -> ResponseBase:
    ''' robots '''
    resp = make_response('''User-agent: *
Allow: /

Sitemap: https://volunteer.coscup.org/sitemap.txt
Sitemap: https://volunteer.coscup.org/docs/sitemap.xml''', 200)
    resp.mimetype = 'text/plain'
    return resp


@app.route('/sitemap.txt')
def sitemap() -> ResponseBase:
    ''' sitemap '''
    result: list[str] = []
    for path in (
        '/',
        '/.well-known/security.txt',
        '/api/docs',
        '/api/redoc',
        '/bug-report',
        '/coc',
        '/doc/security.txt',
        '/docs/sitemap.xml',
        '/privacy',
        '/robots.txt',
        '/security_guard',
    ):
        result.append(f'https://volunteer.coscup.org{path}')

    for path in Tasks.sitemap():
        result.append(f'https://volunteer.coscup.org{path}')

    for path in Track.sitemap():
        result.append(f'https://volunteer.coscup.org{path}')

    for path in TalkFavs(pid='2023', uid='').sitemap():
        result.append(f'https://volunteer.coscup.org{path}')

    resp = make_response('\r\n'.join(result), 200)
    resp.mimetype = 'text/plain'
    return resp


@app.route('/exception')
def exception_func() -> str:
    ''' exception_func '''
    try:
        return str(1/0)
    except Exception as error:
        raise Exception('Error: [{error}]') from error


def error_exception(sender: Any, exception: Any, **extra: Any) -> None:
    ''' error_exception '''
    logging.info('sender: %s, exception: %s, extra: %s',
                 sender, exception, extra)

    mail_sys_weberror.apply_async(
        kwargs={
            'title': f'{request.method}, {request.path}, {arrow.now()}',
            'body': f'''<b>{request.method}</b> {request.path}<br>
<pre>{os.environ}</pre>
<pre>{request.headers}</pre>
<pre>User: {g.get('user', {}).get('account', {}).get('_id')}\n\n
sid: {session.get('sid')}\n\n
args: {request.args}\n\nform: {request.form}\n\n
values: {request.values}\n\n{traceback.format_exc()}</pre>'''
        })


got_request_exception.connect(error_exception, app)
