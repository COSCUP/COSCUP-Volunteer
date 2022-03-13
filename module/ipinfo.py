from requests import Session


class IPInfo(Session):

    def __init__(self, token):
        super(IPInfo, self).__init__()
        self.token = token

    def get(self, ip):
        ''' Get info

        :param str ip: ip

        '''
        headers = {
            'Authorization': 'Bearer %s' % self.token,
        }
        return super(IPInfo, self).get('https://ipinfo.io/%s' % ip,
                                       headers=headers)
