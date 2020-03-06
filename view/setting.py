import math

import arrow
import phonenumbers
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from module.mattermost_link import MattermostLink
from module.mc import MC
from module.users import User
from module.usession import USession
from module.waitlist import WaitList


VIEW_SETTING = Blueprint('setting', __name__, url_prefix='/setting')


@VIEW_SETTING.route('/')
def index():
    return render_template('./setting_index.html')


@VIEW_SETTING.route('/profile', methods=('GET', 'POST'))
def profile():
    if request.method == 'GET':
        user = g.user['account']
        if 'profile' not in user:
            user['profile'] = {}

        return render_template('./setting_profile.html', user=user)
    elif request.method == 'POST':
        data = {
            'badge_name': request.form['badge_name'],
            'intro': request.form['intro'],
        }
        User(uid=g.user['account']['_id']).update_profile(data)
        MC.get_client().delete('sid:%s' % session['sid'])
        return redirect(url_for('setting.profile', _scheme='https', _external=True))


@VIEW_SETTING.route('/profile_real', methods=('GET', 'POST'))
def profile_real():
    if request.method == 'GET':
        user = g.user['account']

        default_code = '886'
        if 'profile_real' not in user:
            user['profile_real'] = {}
        else:
            try:
                phone = phonenumbers.parse(user['profile_real']['phone'], None)
                user['profile_real']['phone'] = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.NATIONAL)

                default_code = phone.country_code

            except phonenumbers.phonenumberutil.NumberParseException:
                pass

        if 'bank' not in user['profile_real']:
            user['profile_real']['bank'] = {}

        phone_codes = sorted(phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items(), key= lambda x: x[1][0])

        return render_template('./setting_profile_real.html', user=user,
                phone_codes=phone_codes, default_code=default_code)

    elif request.method == 'POST':
        try:
            phone = phonenumbers.parse('+%(phone_code)s %(phone)s' % request.form)
            phone = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            phone = ''

        data = {
            'name': request.form['name'].strip(),
            'phone': phone,
            'birthday': request.form['birthday'].strip(),
            'roc_id': request.form['roc_id'].strip(),
            'company': request.form['company'].strip(),
            'bank': {
                'code': request.form['account_bank_code'].strip(),
                'no': request.form['account_bank_no'].strip(),
                'branch': request.form['account_bank_branch'].strip(),
                'name': request.form['account_bank_name'].strip(),
            }
        }

        User(uid=g.user['account']['_id']).update_profile_real(data)
        return redirect(url_for('setting.profile_real', _scheme='https', _external=True))


@VIEW_SETTING.route('/link/chat', methods=('GET', 'POST'))
def link_chat():
    if request.method == 'GET':
        mml = MattermostLink(uid=g.user['account']['_id'])
        return render_template('./setting_link_chat.html', mml=mml)

    elif request.method == 'POST':
        MattermostLink.reset(uid=g.user['account']['_id'])
        return redirect(url_for('setting.link_chat', _scheme='https', _external=True))


@VIEW_SETTING.route('/security', methods=('GET', 'POST'))
def security():
    if request.method == 'GET':
        _now = arrow.now()

        alive_session = []
        for raw in USession.get_alive(uid=g.user['account']['_id']):
            if 'ipinfo' in raw and 'timezone' in raw['ipinfo']:
                timezone = raw['ipinfo']['timezone']
            else:
                timezone = 'Asia/Taipei'

            _created_at = arrow.get(math.ceil(raw['created_at']))
            raw['iso_time'] = _created_at.to(timezone).isoformat()
            raw['time_hr'] = _created_at.humanize(_now)
            raw['is_me'] = raw['_id'] == session['sid']

            alive_session.append(raw)

        records = []
        for raw in USession.get_recently(uid=g.user['account']['_id']):
            if 'ipinfo' in raw and 'timezone' in raw['ipinfo']:
                timezone = raw['ipinfo']['timezone']
            else:
                timezone = 'Asia/Taipei'

            _created_at = arrow.get(math.ceil(raw['created_at']))
            raw['iso_time'] = _created_at.to(timezone).isoformat()
            raw['time_hr'] = _created_at.humanize(_now)

            records.append(raw)

        return render_template('./setting_security.html',
                records=records, alive_session=alive_session)

    elif request.method == 'POST':
        data = request.get_json()
        USession.make_dead(sid=data['sid'], uid=g.user['account']['_id'])

        return jsonify(data)


@VIEW_SETTING.route('/waitting')
def waitting():
    waitting_lists = []

    for raw  in WaitList.find_history(uid=g.user['account']['_id']):
        raw['hr_time'] = arrow.get(raw['_id'].generation_time).to('Asia/Taipei').format('YYYY-MM-DD')

        if 'result' in raw:
            if raw['result'] == 'approval':
                raw['result'] = 'approved'
            elif raw['result'] == 'deny':
                raw['result'] = 'denid'
        else:
            raw['result'] = 'waitting'

        waitting_lists.append(raw)

    waitting_lists = sorted(waitting_lists, key=lambda x: x['_id'], reverse=True)

    return render_template('./setting_waitting.html', waitting_lists=waitting_lists)
