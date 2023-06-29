''' TelegramBot '''
from time import time
from typing import Any, Union, Optional
from uuid import uuid4

from requests import Response, Session

from module.mc import MC


class Telegram(Session):
    ''' Telegram

    Args:
        token (str): API token.

    '''

    def __init__(self, token: str) -> None:
        super().__init__()
        self.url = f'https://api.telegram.org/bot{token}'

    def get_me(self) -> Response:
        ''' Get me '''
        return self.post(f'{self.url}/getMe')

    def send_message(self, chat_id: str, text: str,
                     parse_mode: str = 'Markdown',
                     reply_markup: Union[dict[str, Any], None] = None,
                     protect_content: bool = False,
                     reply_to_message_id: Optional[int] = None,
                     ) -> Response:
        # pylint: disable=too-many-arguments
        ''' Send message

        Args:
            chat_id (str): Chat id.
            text (str): Text.
            parse_mode (str): `Markdown`, `MarkdownV2`, `HTML`.
            reply_markup (dict): Reply markup.
            protect_content (bool): Protects the contents of the sent message
                                    from forwarding and saving.
            reply_to_message_id (int): If the message is a reply, ID of the original message.

        References:
            https://core.telegram.org/bots/api#sendmessage

        '''
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'protect_content': protect_content,
        }  # type: dict[str, Union[str, dict[str, Any], bool, int]]

        if reply_markup is not None:
            data['reply_markup'] = reply_markup

        if reply_to_message_id is not None:
            data['reply_to_message_id'] = reply_to_message_id

        return self.post(f'{self.url}/sendMessage', json=data)

    def set_webhook(self, url: str) -> Response:
        ''' Set webhook

        Args:
            url (str): URL.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.url}/setWebhook', json={'url': url})

    def get_webhook_info(self, url: str) -> Response:
        ''' Get webhook info

        Args:
            url (str): URL.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.url}/getWebhookInfo', json={'url': url})

    def delete_webhook(self) -> Response:
        ''' delete webhook

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.url}/deleteWebhook')

    @staticmethod
    def is_command_start(data: dict[str, Any]) -> bool:
        ''' command start

        Args:
            data (dict): The data from telegram return.

        Returns:
            Check the `message.from.is_bot` ot `message.text`.

        '''
        if data['message']['from']['is_bot']:
            return False

        if data['message']['text'].strip() == '/start':
            return True

        return False

    @staticmethod
    def is_command_start_linkme(data: dict[str, Any]) -> bool:
        ''' command start

        Args:
            data (dict): The data from telegram return.

        Returns:
            Check the `message.from.is_bot` ot `message.text`.

        '''
        if 'message' not in data:
            return False

        if data['message']['from']['is_bot']:
            return False

        if 'text' not in data['message']:
            return False

        if data['message']['text'].strip() in ('/start linkme', '/linkme'):
            return True

        return False


class TelegramBot(Telegram):
    ''' TelegramBot

    Args:
        token (str): API token.

    '''

    def __init__(self, token: str) -> None:
        super().__init__(token=token)

    @staticmethod
    def gen_uuid(chat_id: str, expired_time: int = 300) -> dict[str, Any]:
        ''' Gen uuid for verify

        Args:
            chat_id (str): Chat id.
            expired_time (int): Expired time.

        Returns:
            Return the data.

        '''
        data = {
            'uuid': str(uuid4()),
            'chat_id': chat_id,
            'code': f'{uuid4().fields[0]:08x}',
            'expired': int(time()) + expired_time,
        }

        mem_cache = MC.get_client()
        mem_cache.set(f"tg:{data['uuid']}", data, expired_time)

        return dict(mem_cache.get(f"tg:{data['uuid']}"))

    @staticmethod
    def temp_fetch_user_data(data: dict[str, Any], expired_time: int = 400) -> None:
        ''' temp fetch user data

        Args:
            data (dict): The data to cache.
            expired_time (int): Expired time.

        '''
        mem_cache = MC.get_client()
        mem_cache.set(f"tgu:{data['message']['from']['id']}",
                      data['message']['from'], expired_time)

    @staticmethod
    def get_temp_user_dta(chat_id: str) -> dict[str, Any]:
        ''' Get temp user data

        Args:
            chat_id (str): Chat id.

        Returns:
            Return the data.

        '''
        mem_cache = MC.get_client()

        data = mem_cache.get(f'tgu:{chat_id}')

        if data:
            return dict(data)

        return {}
