''' MattermostBot '''
# pylint: disable=arguments-renamed,arguments-differ
import logging
from typing import Any, Generator, Optional, Union

from requests import Response, Session

from models.mattermost_link_db import MattermostLinkDB
from models.mattermostdb import MattermostUsersDB
from models.oauth_db import OAuthDB
from module.mattermost_link import MattermostLink


class MattermostBot(Session):
    ''' MattermostBot

    Args:
        token (str): API token.
        base_url (str): API base url.
        log_name (str): Log name.

    Note:
        The `headers` will update the `Authorization` in `Bearer {self.token}`.

    '''

    def __init__(self, token: str, base_url: str, log_name: str = 'MattermostBot') -> None:
        super().__init__()
        self.token = token
        self.base_url = base_url
        self.log = logging.getLogger(log_name)
        self.headers.update({'Authorization': f'Bearer {self.token}'})

    def log_rate_limit(self, headers: dict[str, Any]) -> None:
        ''' Get log info from headers

        Args:
            headers (dict): [requests.Response.headers][].

        '''
        self.log.info('X-Ratelimit-Limit: %s, X-Ratelimit-Remaining: %s, X-Ratelimit-Reset: %s',
                      headers.get('X-Ratelimit-Limit'),
                      headers.get('X-Ratelimit-Remaining'),
                      headers.get('X-Ratelimit-Reset'),
                      )

    def get_users(self, page: int, per_page: int = 200) -> Response:
        ''' Get users

        Args:
            page (int): Page.
            per_page (int): Numbers per page.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.get(f'{self.base_url}/users', params={'page': page, 'per_page': per_page})

    def get_users_loop(self, per_page: int = 200) -> Generator[dict[str, Any], None, None]:
        ''' Get users in loop

        Args:
            per_page (int): Numbers per page.

        Yields:
            Yield the user's info.

        '''
        page = 0
        num = 0
        for user in self.get_users(page=page, per_page=per_page).json():
            yield user
            num += 1

        while num == per_page:
            page += 1
            num = 0
            for user in self.get_users(page=page, per_page=per_page).json():
                yield user
                num += 1

    def get_users_stats(self) -> Response:
        ''' Get users stats

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.get(f'{self.base_url}/users/stats')

    def get_user_by_username(self, username: str) -> Response:
        ''' Get user by username

        Args:
            username (str): Username.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.get(f'{self.base_url}/users/username/{username}')

    def create_a_direct_message(self,
                                users: Union[list[str], tuple[str, str]]) -> Response:
        ''' Create a direct messge

        Args:
            users (list | tuple): Two uids in list or tuple.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.base_url}/channels/direct', json=users)

    def posts(self, channel_id: str, message: str) -> Response:
        ''' Posts message

        Args:
            channel_id (str): Channel id.
            message (str): Messages.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.base_url}/posts',
                         json={'channel_id': channel_id, 'message': message})

    def get_posts_from_channel(self, channel_id: str) -> Response:
        ''' Get post from channel

        Args:
            channel_id (str): Channel id.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.get(f'{self.base_url}/channels/{channel_id}/posts')

    def post_invite_by_email(self, team_id: str, emails: list[str]) -> Response:
        ''' Post an invite by email

        Args:
            team_id (str): Team id.
            emails (list): Email addresses.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.base_url}/teams/{team_id}/invite/email', json=emails)

    def post_invite_guests_by_email(self, team_id: str, emails: list[str],
                                    channels: list[str], message: Optional[str] = None) -> Response:
        ''' Post an invite to guest by email

        Args:
            team_id (str): Team id.
            emails (list): Email addresses.
            channels (list): Channel ids.
            message (str): Messages.

        Returns:
            Return the [requests.Response][] object.

        '''
        data: dict[str, Any] = {
            'emails': emails,
            'channels': channels,
        }
        if message:
            data['message'] = message.strip()

        return self.post(f'{self.base_url}/teams/{team_id}/invite-guests/email', json=data)

    def post_user_to_channel(self, channel_id: str, uid: str) -> Response:
        ''' Post user to channel

        Args:
            channel_id (str): Channel id.
            uid (str): User id.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.base_url}/channels/{channel_id}/members', json={'user_id': uid})

    def put_users_patch(self, uid: str, position: str) -> Response:
        ''' Update user

        Args:
            uid (str): User id.
            position (str): Position title.

        Returns:
            Return the [requests.Response][] object.

        '''
        data = {
            'position': position,
        }
        return self.put(f'{self.base_url}/users/{uid}/patch', json=data)

    def post_revoke_all_sessions_for_a_user(self, uid: str) -> Response:
        ''' Revoke all sessions for a user

        Args:
            uid (str): User id.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.post(f'{self.base_url}/users/{uid}/sessions/revoke/all')

    def del_deactivate_user(self, uid: str) -> Response:
        ''' Deactivate user account

        Args:
            uid (str): User id.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.delete(f'{self.base_url}/users/{uid}')


class MattermostTools(MattermostBot):
    ''' MattermostTools for more implement in operation

    Args:
        token (str): API token.
        base_url (str): The API base url.

    '''

    def __init__(self, token: str, base_url: str) -> None:
        super().__init__(token=token, base_url=base_url)

    @staticmethod
    def find_possible_mid(uid: str, mail: Optional[str] = None) -> str:
        ''' Find any possible mattermost user id

        Args:
            uid (str): User id.
            mail (str): User email address.

        Returns:
            Return the user's mattermost id or `''`.

        '''
        mml = MattermostLink(uid)
        if not mml:
            return ''

        if mml.raw and 'data' in mml.raw and 'user_id' in mml.raw['data']:
            return str(mml.raw['data']['user_id'])

        if mail is None:
            oauth = OAuthDB().find_one({'owner': uid}, {'_id': 1})
            if oauth:
                mail = oauth['_id']

        if mail:
            mm_user = MattermostUsersDB().find_one(
                {'email': mail.strip()}, {'_id': 1})
            if mm_user:
                return str(mm_user['_id'])

        return ''

    @staticmethod
    def find_user_name(mid: str) -> str:
        ''' Find user_name by mid

        Args:
            mid (str): Mattermost user id.

        Returns:
            Return the user's mattermost user name or `''`.

        '''
        mm_user = MattermostUsersDB().find_one({'_id': mid}, {'username': 1})
        if mm_user:
            return str(mm_user['username'])

        mattermost_link = MattermostLinkDB().find_one(
            {'data.user_id': mid}, {'data.user_name': 1})
        if mattermost_link and 'data' in mattermost_link:
            return str(mattermost_link['data']['user_name'])

        return ''
