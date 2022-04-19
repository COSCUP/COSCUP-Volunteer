''' MattermostBot '''
# pylint: disable=arguments-renamed,arguments-differ
import logging

from requests import Session

from models.mattermost_link_db import MattermostLinkDB
from models.mattermostdb import MattermostUsersDB
from models.oauth_db import OAuthDB
from module.mattermost_link import MattermostLink


class MattermostBot(Session):
    ''' MattermostBot '''

    def __init__(self, token, base_url, log_name='MattermostBot'):
        super().__init__()
        self.token = token
        self.base_url = base_url
        self.log = logging.getLogger(log_name)

    def log_rate_limit(self, headers):
        ''' Get log info from headers '''
        self.log.info('X-Ratelimit-Limit: %s, X-Ratelimit-Remaining: %s, X-Ratelimit-Reset: %s',
                      headers.get('X-Ratelimit-Limit'),
                      headers.get('X-Ratelimit-Remaining'),
                      headers.get('X-Ratelimit-Reset'),
                      )

    def get(self, path, **kwargs):
        headers = {'Authorization': f'Bearer {self.token}'}
        resp = super().get(f'{self.base_url}{path}', headers=headers, **kwargs)
        self.log_rate_limit(resp.headers)
        return resp

    def post(self, path, **kwargs):
        headers = {'Authorization': f'Bearer {self.token}'}
        resp = super().post(f'{self.base_url}{path}',
                            headers=headers, **kwargs)
        self.log_rate_limit(resp.headers)
        return resp

    def put(self, path, **kwargs):
        headers = {'Authorization': f'Bearer {self.token}'}
        resp = super().put(f'{self.base_url}{path}', headers=headers, **kwargs)
        self.log_rate_limit(resp.headers)
        return resp

    def get_users(self, page, per_page=200):
        ''' Get users '''
        return self.get('/users', params={'page': page, 'per_page': per_page})

    def get_users_loop(self, per_page=200):
        ''' Get users in loop '''
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

    def get_users_stats(self):
        ''' Get users stats '''
        return self.get('/users/stats')

    def get_user_by_username(self, username):
        ''' Get user by username '''
        return self.get(f'/users/username/{username}')

    def create_a_direct_message(self, users):
        ''' Create a direct messge '''
        return self.post('/channels/direct', json=users)

    def posts(self, channel_id, message):
        ''' Posts message '''
        return self.post('/posts', json={'channel_id': channel_id, 'message': message})

    def get_posts_from_channel(self, channel_id):
        ''' Get post from channel '''
        return self.get(f'/channels/{channel_id}/posts')

    def post_invite_by_email(self, team_id, emails):
        ''' Post an invite by email '''
        return self.post(f'/teams/{team_id}/invite/email', json=emails)

    def post_invite_guests_by_email(self, team_id, emails, channels, message=None):
        ''' Post an invite to guest by email '''
        data = {
            'emails': emails,
            'channels': channels,
        }
        if message:
            data['message'] = message.strip()

        return self.post(f'/teams/{team_id}/invite-guests/email', json=data)

    def post_user_to_channel(self, channel_id, uid):
        ''' Post user to channel '''
        return self.post(f'/channels/{channel_id}/members', json={'user_id': uid})

    def put_users_patch(self, uid, position):
        ''' Update user '''
        data = {
            'position': position,
        }
        return self.put(f'/users/{uid}/patch', json=data)


class MattermostTools(MattermostBot):
    ''' MattermostTools for more implement in operation '''

    def __init__(self, token, base_url):
        super().__init__(token=token, base_url=base_url)

    @staticmethod
    def find_possible_mid(uid, mail=None):
        ''' Find any possible mattermost user id

        :param str uid: uid
        :param str mail: user mail

        '''
        mml = MattermostLink(uid)
        if not mml:
            return ''

        if 'data' in mml.raw and 'user_id' in mml.raw['data']:
            return mml.raw['data']['user_id']

        if mail is None:
            oauth = OAuthDB().find_one({'owner': uid}, {'_id': 1})
            if oauth:
                mail = oauth['_id']

        if mail:
            mm_user = MattermostUsersDB().find_one(
                {'email': mail.strip()}, {'_id': 1})
            if mm_user:
                return mm_user['_id']

        return ''

    @staticmethod
    def find_user_name(mid):
        ''' Find user_name by mid

        :param str mid: mid

        '''
        mm_user = MattermostUsersDB().find_one({'_id': mid}, {'username': 1})
        if mm_user:
            return mm_user['username']

        mattermost_link = MattermostLinkDB().find_one(
            {'data.user_id': mid}, {'data.user_name': 1})
        if mattermost_link and 'data' in mattermost_link:
            return mattermost_link['data']['user_name']

        return ''
