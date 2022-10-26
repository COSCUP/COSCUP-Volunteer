''' Telegram '''
import logging

import arrow
from flask import Blueprint, g, redirect, request, url_for
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

import setting
from models.telegram_db import TelegramDB
from module.mc import MC
from module.telegram_bot import TelegramBot

VIEW_TELEGRAM = Blueprint('telegram', __name__, url_prefix='/telegram')


@VIEW_TELEGRAM.route('/r', methods=('POST', ))
def receive() -> ResponseBase:
    ''' receive '''
    data = request.get_json()
    logging.info('[telegram] %s', data)

    if data and TelegramBot.is_command_start_linkme(data):
        uuid_data = TelegramBot.gen_uuid(chat_id=data['message']['from']['id'])
        TelegramBot.temp_fetch_user_data(data=data)

        resp = TelegramBot(token=setting.TELEGRAM_TOKEN).send_message(
            chat_id=data['message']['from']['id'],
            text='請繼續前往志工平台登入驗證，感謝！',
            reply_markup={
                'inline_keyboard': [
                    [{'text': '驗證（verify）',
                      'url': f"https://{setting.DOMAIN}/telegram/verify/{uuid_data['uuid']}"}, ],
                ]},
        )

        logging.info('[Telegram][Send] %s', resp.json())

    return Response('', status=200)


@VIEW_TELEGRAM.route('/verify/<tg_uuid>', methods=('GET', 'POST'))
def link_telegram_verify(tg_uuid: str) -> ResponseBase:
    ''' Link Telegram verify '''
    if request.method == 'GET':
        mem_cache = MC.get_client()
        data = mem_cache.get(f'tg:{tg_uuid}')
        if not data:
            return Response('Expired. `/linkme` again', status=406)

        user_data = mem_cache.get(f"tgu:{data['chat_id']}")
        if data and user_data:
            save_data = {'uid': g.user['account']
                         ['_id'], 'added': arrow.now().naive}
            save_data.update(user_data)
            TelegramDB().add(save_data)

            TelegramBot(token=setting.TELEGRAM_TOKEN).send_message(
                chat_id=save_data['id'],
                text='與 [%(uid)s](https://volunteer.coscup.org/user/%(uid)s) 完成帳號綁定！（Completed）' % save_data)  # pylint: disable=line-too-long

            mem_cache.delete_multi(
                [f'tg:{tg_uuid}', f"tgu:{g.user['account']['_id']}"])

            logging.info('[Telegram][Send] linkme: %s %s',
                         save_data['id'], save_data['uid'])

            return redirect(url_for('setting.link_telegram', _scheme='https', _external=True))

        return Response('Expired. `/linkme` again', status=406)

    return Response('', status=404)
