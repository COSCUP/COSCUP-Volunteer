from time import time
from uuid import uuid4

from requests.sessions import Session

from module.mc import MC


class TelegramBot(Session):
    def __init__(self, token):
        super(TelegramBot, self).__init__()
        self.url = 'https://api.telegram.org/bot%s' % token

    def get(self, path, **kwargs):
        ''' GET '''
        return super(TelegramBot, self).get(self.url+path, **kwargs)

    def post(self, path, **kwargs):
        ''' POST '''
        return super(TelegramBot, self).post(self.url+path, **kwargs)

    def get_me(self):
        ''' Get me '''
        return self.post('/getMe')

    def send_message(self, chat_id, text, parse_mode='Markdown', reply_markup=None):
        ''' Send message '''
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        if reply_markup is not None:
            data['reply_markup'] = reply_markup

        return self.post('/sendMessage', json=data)

    def set_webhook(self, url):
        ''' Set webhook '''
        return self.post('/setWebhook', json={'url': url})

    def get_webhook_info(self, url):
        ''' Get webhook info '''
        return self.post('/getWebhookInfo', json={'url': url})

    def delete_webhook(self):
        ''' delete webhook '''
        return self.post('/deleteWebhook')

    @staticmethod
    def is_command_start(data: dict) -> bool:
        ''' command start '''
        if data['message']['from']['is_bot']:
            return False

        if data['message']['text'].strip() == '/start':
            return True

        return False

    @staticmethod
    def is_command_start_linkme(data: dict) -> bool:
        ''' command start '''
        if 'message' not in data:
            return False

        if data['message']['from']['is_bot']:
            return False

        if data['message']['text'].strip() in ('/start linkme', '/linkme'):
            return True

        return False

    @staticmethod
    def gen_uuid(chat_id, expired_time=300) -> dict:
        ''' Gen uuid for verify '''
        data = {
            'uuid': str(uuid4()),
            'chat_id': chat_id,
            'code': '%0.8x' % uuid4().fields[0],
            'expired': int(time()) + expired_time,
        }

        mc = MC.get_client()
        mc.set('tg:%s' % data['uuid'], data, expired_time)

        return mc.get('tg:%s' % data['uuid'])

    @staticmethod
    def temp_fetch_user_data(data, expired_time=400):
        ''' temp fetch user data '''
        mc = MC.get_client()
        mc.set('tgu:%s' % data['message']['from']['id'],
               data['message']['from'], expired_time)

    @staticmethod
    def get_temp_user_dta(chat_id):
        ''' Get temp user data '''
        mc = MC.get_client()
        return mc.get('tgu:%s' % chat_id)
