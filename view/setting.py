''' setting '''
import json
import math
from typing import Any, Callable

import arrow
import phonenumbers
from flask import (Blueprint, g, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

from celery_task.task_service_sync import service_sync_mattermost_invite
from celery_task.task_mail_sys import mail_member_welcome_send
from models.telegram_db import TelegramDB
from module.api_token import APIToken, APITokenTemp
from module.dietary_habit import (DietaryHabitItemsName,
                                  DietaryHabitItemsValue, valid_dietary_value)
from module.mattermost_link import MattermostLink
from module.mc import MC
from module.skill import (SkillEnum, SkillEnumDesc, StatusEnum, StatusEnumDesc,
                          TeamsEnum, TeamsEnumDesc, TobeVolunteerStruct)
from module.users import TobeVolunteer, User
from module.usession import USession
from module.waitlist import WaitList
from structs.users import UserAddress, UserBank, UserProfle, UserProfleReal

VIEW_SETTING = Blueprint('setting', __name__, url_prefix='/setting')


@VIEW_SETTING.route('/')
def index() -> str:
    ''' Index page '''
    return render_template('./setting_index.html')


@VIEW_SETTING.route('/profile', methods=('GET', 'POST'))
def profile_page() -> str | ResponseBase:
    ''' profile '''
    # pylint: disable=too-many-branches
    if request.method == 'GET':
        user = g.user['account']
        if 'profile' not in user:
            user['profile'] = UserProfle().dict()

        return render_template('./setting_profile.html', user=user)

    if request.method == 'POST':
        post_data = request.get_json()

        if post_data and post_data['casename'] == 'get':
            user = g.user['account']
            if 'profile' not in user:
                user['profile'] = UserProfle().dict()

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

        if post_data and post_data['casename'] == 'get_tobe_volunteer':
            data = TobeVolunteer.get(uid=g.user['account']['_id'])

            return jsonify({'tobe_volunteer': data.dict()})

        if post_data and post_data['casename'] == 'save_tobe_volunteer':
            save_data = TobeVolunteerStruct.parse_obj(post_data['data']).dict()
            save_data['uid'] = g.user['account']['_id']
            TobeVolunteer.save(data=save_data)

            return jsonify({})

        if post_data and post_data['casename'] == 'save':
            User(uid=g.user['account']['_id']).update_profile(
                UserProfle.parse_obj(post_data['data']).dict()
            )
            MC.get_client().delete(f"sid:{session['sid']}")

        return jsonify({})

    return make_response({}, 404)


@VIEW_SETTING.route('/profile_real', methods=('GET', 'POST'))
def profile_real() -> str | ResponseBase:
    ''' Profile real '''
    # pylint: disable=too-many-branches
    if request.method == 'GET':
        return render_template('./setting_profile_real.html')

    if request.method == 'POST':
        post_data = request.get_json()
        struct_user: UserProfleReal

        if post_data and post_data['casename'] == 'get':
            default_code: str = '886'

            if 'profile_real' in g.user['account']:
                user = {'profile_real': g.user['account']['profile_real']}

                struct_user = UserProfleReal.parse_obj(
                    g.user['account']['profile_real'])

                try:
                    phone = phonenumbers.parse(struct_user.phone, None)
                    struct_user.phone = phonenumbers.format_number(
                        phone, phonenumbers.PhoneNumberFormat.NATIONAL)
                    default_code = str(
                        phone.country_code) if phone.country_code else '886'

                except phonenumbers.phonenumberutil.NumberParseException:
                    pass
            else:
                struct_user = UserProfleReal()

            user = struct_user.dict()

            if 'birthday' in user and user['birthday']:
                user['birthday'] = user['birthday'].strftime(
                    '%Y-%m-%d')

            phone_codes = sorted(
                phonenumbers.COUNTRY_CODE_TO_REGION_CODE.items(), key=lambda x: x[1][0])

            dietary_habit_list = []
            for item in DietaryHabitItemsName:
                dietary_habit_list.append(
                    (DietaryHabitItemsValue[item.name].value, item.value))

            return jsonify({'profile': user,
                            'phone_codes': phone_codes,
                            'default_code': default_code,
                            'dietary_habit': dietary_habit_list,
                            })

        if post_data and post_data['casename'] == 'update':
            phone_str = ''
            if 'phone' in post_data['data'] and post_data['data']['phone'] and \
                    'phone_code' in post_data['data'] and post_data['data']['phone_code']:
                try:
                    phone_number = phonenumbers.parse(
                        f"+{post_data['data']['phone_code']} {post_data['data']['phone']}")
                    phone_str = phonenumbers.format_number(
                        phone_number, phonenumbers.PhoneNumberFormat.E164)
                except phonenumbers.phonenumberutil.NumberParseException:
                    phone_str = ''

            user_profile_real = UserProfleReal(
                name=post_data['data'].get('name'),
                phone=phone_str,
                roc_id=post_data['data'].get('roc_id'),
                company=post_data['data'].get('company')
            )

            try:
                birthday = arrow.get(post_data['data'].get(
                    'birthday', '').strip()).naive
            except (AttributeError, arrow.parser.ParserError):
                birthday = None

            user_profile_real.birthday = birthday

            user_profile_real.dietary_habit = valid_dietary_value(
                items_no=post_data['data']['dietary_habit'])

            user_profile_real.bank = UserBank.parse_obj(
                post_data['data']['bank'])

            user_profile_real.address = UserAddress.parse_obj(
                post_data['data']['address'])

            User(uid=g.user['account']['_id']).update_profile_real(
                user_profile_real.dict(exclude_none=True))
            MC.get_client().delete(f"sid:{session['sid']}")

            return jsonify(user_profile_real.dict(exclude_none=True))

    return make_response({}, 404)


@VIEW_SETTING.route('/link/chat', methods=('GET', 'POST'))
def link_chat() -> str | ResponseBase:
    ''' Link to chat '''
    if request.method == 'GET':
        mml = MattermostLink(uid=g.user['account']['_id'])
        return render_template('./setting_link_chat.html', mml=mml)

    if request.method == 'POST':
        data = request.get_json()
        if data and 'casename' in data:
            if data['casename'] == 'invite':
                service_sync_mattermost_invite.apply_async(
                    kwargs={'uids': (g.user['account']['_id'], )})
                return jsonify({})
        else:
            MattermostLink.reset(uid=g.user['account']['_id'])
            return redirect(url_for('setting.link_chat', _scheme='https', _external=True))

    return Response('', status=404)


@VIEW_SETTING.route('/link/telegram', methods=('GET', 'POST'))
def link_telegram() -> str | ResponseBase:
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
        if data and 'casename' in data and data['casename'] == 'del_account':
            TelegramDB().delete_many({'uid': g.user['account']['_id']})

        return jsonify({})

    return make_response({}, 404)


@VIEW_SETTING.route('/security', methods=('GET', 'POST'))
def security() -> str | ResponseBase:
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
        if data:
            USession.make_dead(sid=data['sid'], uid=g.user['account']['_id'])
            return jsonify({})

    return make_response({}, 404)


@VIEW_SETTING.route('/waitting')
def waitting() -> str:
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

    call_func_id: Callable[[
        dict[str, Any], ], Any] = lambda x: x['_id']
    waitting_lists = sorted(
        waitting_lists, key=call_func_id, reverse=True)

    return render_template('./setting_waitting.html', waitting_lists=waitting_lists)


@VIEW_SETTING.route('/api_token', methods=('GET', 'POST'))
def api_token() -> str | ResponseBase:
    ''' API Token'''
    if request.method == 'GET':
        return render_template('./setting_api_token.html')

    if request.method == 'POST':
        data = request.get_json()
        if data and data['casename'] == 'get':
            temp_account = APITokenTemp(uid=g.user['account']['_id'])
            APIToken.save_temp(data=temp_account)

            return jsonify({'temp_account': {
                'username': temp_account.username,
                'password': temp_account.password,
            }})

    return make_response({}, 404)


@VIEW_SETTING.route('/mails', methods=('GET', 'POST'))
def mails() -> str | ResponseBase:
    ''' about mails '''
    if request.method == 'GET':
        return render_template('./setting_mails.html')

    if request.method == 'POST':
        mail_member_welcome_send.apply_async(kwargs={
            'uids': [g.user['account']['_id'], ]})

        return jsonify({})

    return make_response({}, 404)
