''' setting '''
import json
import math
from typing import Text, Union

import arrow
import phonenumbers
from flask import (Blueprint, Response, g, jsonify, redirect, render_template,
                   request, session, url_for)

from celery_task.task_service_sync import service_sync_mattermost_invite
from models.telegram_db import TelegramDB
from module.dietary_habit import DietaryHabit
from module.mattermost_link import MattermostLink
from module.mc import MC
from module.skill import (SkillEnum, SkillEnumDesc, StatusEnum, StatusEnumDesc,
                          TeamsEnum, TeamsEnumDesc, TobeVolunteerStruct)
from module.users import TobeVolunteer, User
from module.usession import USession
from module.waitlist import WaitList

VIEW_SETTING = Blueprint('setting', __name__, url_prefix='/setting')


@VIEW_SETTING.route('/')
def index() -> Text:
    ''' Index page '''
    return render_template('./setting_index.html')


@VIEW_SETTING.route('/profile', methods=('GET', 'POST'))
def profile_page() -> Union[Text, Response]:
    ''' profile '''
    # pylint: disable=too-many-branches
    if request.method == 'GET':
        user = g.user['account']
        if 'profile' not in user:
            user['profile'] = {}

        return render_template('./setting_profile.html', user=user)

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            user = g.user['account']
            if 'profile' not in user:
                user['profile'] = {}

            profile = {}
            if 'profile' in user:
                if 'badge_name' in user['profile'] and user['profile']['badge_name'].strip():
                    profile['badge_name'] = user['profile']['badge_name'].strip()

                profile['intro'] = user['profile'].get('intro', '')
                profile['id'] = user['_id']

            return jsonify({
                'profile': profile,
                'team_enum': {key: item.value for key, item in TeamsEnum.__members__.items()},
                'team_enum_desc': {key: item.value for key, item in
                                   TeamsEnumDesc.__members__.items()},
                'skill_enum': {key: item.value for key, item in
                               SkillEnum.__members__.items()},
                'skill_enum_desc': {key: item.value for key, item in
                                    SkillEnumDesc.__members__.items()},
                'status_enum': {key: item.value for key, item in StatusEnum.__members__.items()},
                'status_enum_desc': {key: item.value for key, item in
                                     StatusEnumDesc.__members__.items()},
            })

        if post_data['casename'] == 'get_tobe_volunteer':
            data = TobeVolunteer.get(uid=g.user['account']['_id'])

            return jsonify({'tobe_volunteer': data})

        if post_data['casename'] == 'save_tobe_volunteer':
            data = TobeVolunteerStruct.parse_obj(post_data['data']).dict()
            data['uid'] = g.user['account']['_id']
            TobeVolunteer.save(data=data)

            return jsonify({})

        if post_data['casename'] == 'save':
            data = {}
            if 'badge_name' in post_data['data'] and post_data['data']['badge_name']:
                data['badge_name'] = post_data['data']['badge_name'].strip()

            if 'intro' in post_data['data'] and post_data['data']['intro']:
                data['intro'] = post_data['data']['intro'].strip()

            if data:
                User(uid=g.user['account']['_id']).update_profile(data)
                MC.get_client().delete(f"sid:{session['sid']}")

        return jsonify({})

    return jsonify({}), 404


@VIEW_SETTING.route('/profile_real', methods=('GET', 'POST'))
def profile_real():
    ''' Profile real '''
    # pylint: disable=too-many-branches
    if request.method == 'GET':
        return render_template('./setting_profile_real.html')

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'get':
            default_code = '886'

            if 'profile_real' in g.user['account']:
                user = {'profile_real': g.user['account']['profile_real']}

                try:
                    phone = phonenumbers.parse(
                        user['profile_real']['phone'], None)
                    user['profile_real']['phone'] = phonenumbers.format_number(
                        phone, phonenumbers.PhoneNumberFormat.NATIONAL)

                    default_code = phone.country_code

                except phonenumbers.phonenumberutil.NumberParseException:
                    pass
            else:
                user = {'profile_real': {}}

            if 'bank' not in user['profile_real']:
                user['profile_real']['bank'] = {}

            if 'address' not in user['profile_real']:
                user['profile_real']['address'] = {}

            if 'dietary_habit' not in user['profile_real']:
                user['profile_real']['dietary_habit'] = []

            phone_codes = sorted(
                phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items(), key=lambda x: x[1][0])

            return jsonify({'profile': user['profile_real'],
                            'phone_codes': phone_codes,
                            'default_code': default_code,
                            'dietary_habit': list(DietaryHabit.ITEMS.items()),
                            })

        if post_data['casename'] == 'update':
            phone = ''
            if 'phone' in post_data['data'] and post_data['data']['phone'] and \
                    'phone_code' in post_data['data'] and post_data['data']['phone_code']:
                try:
                    phone = phonenumbers.parse(
                        f"+{post_data['data']['phone_code']} {post_data['data']['phone']}")
                    phone = phonenumbers.format_number(
                        phone, phonenumbers.PhoneNumberFormat.E164)
                except phonenumbers.phonenumberutil.NumberParseException:
                    phone = ''

            data = {
                'name': post_data['data'].get('name', '').strip(),
                'phone': phone,
                'roc_id': post_data['data'].get('roc_id', '').strip(),
                'company': post_data['data'].get('company', '').strip(),
                'dietary_habit': DietaryHabit.valid(items_no=post_data['data']['dietary_habit']),
                'bank': {
                    'code': post_data['data']['bank'].get('code', '').strip(),
                    'no': post_data['data']['bank'].get('no', '').strip(),
                    'branch': post_data['data']['bank'].get('branch', '').strip(),
                    'name': post_data['data']['bank'].get('name', '').strip(),
                },
                'address': {
                    'code': post_data['data']['address'].get('code', '').strip(),
                    'receiver': post_data['data']['address'].get('receiver', '').strip(),
                    'address': post_data['data']['address'].get('address', '').strip(),
                }
            }

            birthday = post_data['data'].get('birthday', '').strip()
            if birthday:
                try:
                    birthday = arrow.get(birthday).format('YYYY-MM-DD')
                except arrow.parser.ParserError:
                    birthday = ''

            data['birthday'] = birthday

            User(uid=g.user['account']['_id']).update_profile_real(data)
            MC.get_client().delete(f"sid:{session['sid']}")

            return jsonify(data)

    return jsonify({}), 404


@VIEW_SETTING.route('/link/chat', methods=('GET', 'POST'))
def link_chat():
    ''' Link to chat '''
    if request.method == 'GET':
        mml = MattermostLink(uid=g.user['account']['_id'])
        return render_template('./setting_link_chat.html', mml=mml)

    if request.method == 'POST':
        data = request.get_json()
        if 'casename' in data:
            if data['casename'] == 'invite':
                service_sync_mattermost_invite.apply_async(
                    kwargs={'uids': (g.user['account']['_id'], )})
                return jsonify(data)
        else:
            MattermostLink.reset(uid=g.user['account']['_id'])
            return redirect(url_for('setting.link_chat', _scheme='https', _external=True))

    return '', 404


@VIEW_SETTING.route('/link/telegram', methods=('GET', 'POST'))
def link_telegram():
    ''' Link to Telegram '''
    if request.method == 'GET':
        telegram_data = []
        for tg_info in TelegramDB().find({'uid': g.user['account']['_id']}):
            tg_info['added'] = arrow.get(tg_info['added']).isoformat()
            telegram_data.append(tg_info)

        return render_template('./setting_link_telegram.html',
                               telegram_data=json.dumps(telegram_data))

    if request.method == 'POST':
        data = request.get_json()
        if 'casename' in data and data['casename'] == 'del_account':
            TelegramDB().delete_many({'uid': g.user['account']['_id']})

        return jsonify({})

    return jsonify({}), 404


@VIEW_SETTING.route('/security', methods=('GET', 'POST'))
def security():
    ''' security '''
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

    if request.method == 'POST':
        data = request.get_json()
        USession.make_dead(sid=data['sid'], uid=g.user['account']['_id'])

        return jsonify(data)

    return jsonify({}), 404


@VIEW_SETTING.route('/waitting')
def waitting():
    ''' waiting, the `waitting` is typo '''
    waitting_lists = []

    for raw in WaitList.find_history(uid=g.user['account']['_id']):
        raw['hr_time'] = arrow.get(raw['_id'].generation_time).to(
            'Asia/Taipei').format('YYYY-MM-DD')

        if 'result' in raw:
            if raw['result'] == 'approval':
                raw['result'] = 'approved'
            elif raw['result'] == 'deny':
                raw['result'] = 'denid'
        else:
            raw['result'] = 'waitting'

        waitting_lists.append(raw)

    waitting_lists = sorted(
        waitting_lists, key=lambda x: x['_id'], reverse=True)

    return render_template('./setting_waitting.html', waitting_lists=waitting_lists)
