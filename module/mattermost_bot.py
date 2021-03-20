import logging

from requests import Session

import setting
from models.mattermost_link_db import MattermostLinkDB
from models.mattermostdb import MattermostUsersDB
from models.oauth_db import OAuthDB
from module.mattermost_link import MattermostLink


class MattermostBot(Session):
    def __init__(self, token, base_url, log_name='MattermostBot'):
        super(MattermostBot, self).__init__()
        self.token = token
        self.base_url = base_url
        self.log = logging.getLogger(log_name)

    def log_rate_limit(self, headers):
        ''' Get log info from headers '''
        self.log.info('X-Ratelimit-Limit: %s, X-Ratelimit-Remaining: %s, X-Ratelimit-Reset: %s' % (
                headers.get('X-Ratelimit-Limit'),
                headers.get('X-Ratelimit-Remaining'),
                headers.get('X-Ratelimit-Reset'),
            ))

    def get(self, path, **kwargs):
        headers = {'Authorization': 'Bearer %s' % self.token}
        r = super(MattermostBot, self).get('%s%s' % (self.base_url, path), headers=headers, **kwargs)
        self.log_rate_limit(r.headers)
        return r

    def post(self, path, **kwargs):
        headers = {'Authorization': 'Bearer %s' % self.token}
        r = super(MattermostBot, self).post('%s%s' % (self.base_url, path), headers=headers, **kwargs)
        self.log_rate_limit(r.headers)
        return r

    def put(self, path, **kwargs):
        headers = {'Authorization': 'Bearer %s' % self.token}
        r = super(MattermostBot, self).put('%s%s' % (self.base_url, path), headers=headers, **kwargs)
        self.log_rate_limit(r.headers)
        return r

    def get_users(self, page, per_page=200):
        return self.get('/users', params={'page': page, 'per_page': per_page})

    def get_users_loop(self, per_page=200):
        page = 0
        n = 0
        for u in self.get_users(page=page, per_page=per_page).json():
            yield u
            n += 1

        while(n == per_page):
            page += 1
            n = 0
            for u in self.get_users(page=page, per_page=per_page).json():
                yield u
                n += 1

    def get_users_stats(self):
        return self.get('/users/stats')

    def get_user_by_username(self, username):
        return self.get('/users/username/%s' % username)

    def create_a_direct_message(self, users):
        return self.post('/channels/direct', json=users)

    def posts(self, channel_id, message):
        return self.post('/posts', json={'channel_id': channel_id, 'message': message})

    def get_posts_from_channel(self, channel_id):
        return self.get('/channels/%s/posts' % channel_id)

    def post_invite_by_email(self, team_id, emails):
        return self.post('/teams/%s/invite/email' % team_id, json=emails)

    def post_invite_guests_by_email(self, team_id, emails, channels, message=None):
        data = {
            'emails': emails,
            'channels': channels,
        }
        if message:
            data['message'] = message.strip()

        return self.post('/teams/%s/invite-guests/email' % team_id, json=data)

    def post_user_to_channel(self, channel_id, uid):
        return self.post('/channels/%s/members' % channel_id, json={'user_id': uid})

    def put_users_patch(self, uid, position):
        data = {
            'position': position,
        }
        return self.put('/users/%s/patch' % uid, json=data)


class MattermostTools(MattermostBot):
    ''' MattermostTools for more implement in operation '''
    def __init__(self, token, base_url):
        super(MattermostTools, self).__init__(token=token, base_url=base_url)

    @staticmethod
    def find_possible_mid(uid, mail=None):
        ''' Find any possible mattermost user id

        :param str uid: uid
        :param str mail: user mail

        '''
        mml = MattermostLink(uid)
        if not mml:
            return u''

        if 'data' in mml.raw and 'user_id' in mml.raw['data']:
            return mml.raw['data']['user_id']

        if mail is None:
            oauth = OAuthDB().find_one({'owner': uid}, {'_id': 1})
            if oauth:
                mail = oauth['_id']

        if mail:
            mm_user = MattermostUsersDB().find_one({'email': mail.strip()}, {'_id': 1})
            if mm_user:
                return mm_user['_id']

        return u''

    @staticmethod
    def find_user_name(mid):
        ''' Find user_name by mid

        :param str mid: mid

        '''
        ml = MattermostLinkDB().find_one({'data.user_id': mid}, {'data.user_name': 1})
        if ml and 'data' in ml:
            return ml['data']['user_name']

        mm_user = MattermostUsersDB().find_one({'_id': mid}, {'username': 1})
        if mm_user:
            return mm_user['username']

        return u''
