from models.base import DBBase


class OAuthDB(DBBase):
    ''' OAuthDB Collection '''
    def __init__(self):
        super(OAuthDB, self).__init__('oauth')

    def index(self):
        ''' Index '''
        self.create_index([('owner', 1), ])

    def add_data(self, mail, data):
        ''' Add user data

        :param str mail: email
        :param dict data: user data

        '''
        self.find_one_and_update(
            {'_id': mail},
            {'$set': {'data': data}},
            upsert=True)

    def add_token(self, mail, credentials):
        ''' Add user oauth token

        :param str mail: email
        :param dict credentials: user oauth token, from ``flow.credentials``

        .. note:: Not to save ``client_id``, ``client_secret``

        '''
        oauth = self.find_one({'_id': mail}, {'token': 1})
        if oauth and 'token' in oauth:
            data = oauth['token']
        else:
            data = {}

        data['token'] = credentials.token
        if credentials.refresh_token:
            data['refresh_token'] = credentials.refresh_token

        data['token_uri'] = credentials.token_uri
        data['id_token'] = credentials.id_token
        data['scopes'] = credentials.scopes

        self.find_one_and_update(
            {'_id': mail},
            {'$set': {'token': data}},
            upsert=True)

    def setup_owner(self, mail, uid):
        ''' Setup owner

        :param str mail: mail
        :param str uid: uid

        '''
        OAuthDB().find_one_and_update({'_id': mail}, {'$set': {'owner': uid}})
