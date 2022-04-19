''' OAuth '''
from models.oauth_db import OAuthDB


class OAuth:
    ''' OAuth

    :param str mail: mail

    '''

    def __init__(self, mail):
        self.mail = mail

    def get(self):
        ''' Get data '''
        return OAuthDB().find_one({'_id': self.mail})

    @staticmethod
    def add(mail, data=None, token=None):
        ''' add data, token

        :param str mail: mail
        :param dict data: return user data
        :param dict token: oauth token data

        '''

        if any((data, token)):
            oauth_db = OAuthDB()

        if data is not None:
            oauth_db.add_data(mail, data)

        if token is not None:
            oauth_db.add_token(mail, token)

    @staticmethod
    def owner(mail):
        ''' return the owner

        :param str mail: mail
        :rtype: str or None

        '''
        data = OAuthDB().find_one({'_id': mail}, {'owner': 1})
        if not data:
            raise Exception(f'No oauth data of `{mail}`')

        return data.get('owner')
