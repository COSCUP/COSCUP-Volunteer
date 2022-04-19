''' IPInfo '''
# pylint: disable=arguments-renamed,arguments-differ
from requests import Session


class IPInfo(Session):
    ''' IPInfo '''

    def __init__(self, token):
        super().__init__()
        self.token = token

    def get(self, ip):
        ''' Get info

        :param str ip: ip

        '''
        headers = {
            'Authorization': f'Bearer {self.token}',
        }
        return super().get(f'https://ipinfo.io/{ip}', headers=headers)
