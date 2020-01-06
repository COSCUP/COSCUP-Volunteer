from models.oauth_db import OAuthDB


class OAuth(object):
    ''' OAuth '''

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
            raise Exception('No oauth data of `%s`' % mail)

        return data.get('owner')
