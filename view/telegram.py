import logging

import arrow
from flask import Blueprint
from flask import g
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for

import setting
from models.telegram_db import TelegramDB
from module.mc import MC
from module.telegram_bot import TelegramBot

VIEW_TELEGRAM = Blueprint('telegram', __name__, url_prefix='/telegram')


@VIEW_TELEGRAM.route('/r', methods=('POST', ))
def receive():
    data = request.get_json()
    logging.info('[telegram] %s' % data)

    if TelegramBot.is_command_start_linkme(data):
        uuid_data = TelegramBot.gen_uuid(chat_id=data['message']['from']['id'])
        TelegramBot.temp_fetch_user_data(data=data)

        r = TelegramBot(token=setting.TELEGRAM_TOKEN).send_message(
                chat_id=data['message']['from']['id'],
                text=u'請繼續前往志工平台登入驗證，感謝！',
                reply_markup={
                        'inline_keyboard': [
                            [{'text': u'驗證（verify）', 'url': 'https://%s/telegram/verify/%s' % (setting.DOMAIN, uuid_data['uuid'])}, ],
                        ]},
            )

        logging.info('[Telegram][Send] %s' % r.json())

    return u'', 200


@VIEW_TELEGRAM.route('/verify/<tg_uuid>', methods=('GET', 'POST'))
def link_telegram_verify(tg_uuid):
    if request.method == 'GET':
        mc = MC.get_client()
        data = mc.get('tg:%s' % tg_uuid)
        if not data:
            return u'Expired. `/linkme` again', 406

        user_data = mc.get('tgu:%s' % data['chat_id'])
        if data and user_data:
            save_data = {'uid': g.user['account']['_id'], 'added': arrow.now().datetime}
            save_data.update(user_data)
            TelegramDB().save(save_data)

            r = TelegramBot(token=setting.TELEGRAM_TOKEN).send_message(
                    chat_id=save_data['id'],
                    text=u'與 [%(uid)s](https://volunteer.coscup.org/user/%(uid)s) 完成帳號綁定！（Completed）' % save_data)

            mc.delete_multi(['tg:%s' % tg_uuid, 'tgu:%s' % g.user['account']['_id']])

            logging.info('[Telegram][Send] linkme: %(id)s %(uid)s' % save_data)

            return redirect(url_for('setting.link_telegram', _scheme='https', _external=True))

        return u'Expired. `/linkme` again', 406

