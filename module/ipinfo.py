''' IPInfo '''
from requests import Response, Session


class IPInfo(Session):
    ''' IPInfo '''

    def __init__(self, token: str):
        super().__init__()
        self.url = 'https://ipinfo.io/'
        self.token = token
        self.headers.update({'Authorization': f'Bearer {self.token}'})

    def get_info(self, ip_address: str) -> Response:
        ''' Get info

        :param str ip: ip

        '''
        return super().get(f'{self.url}{ip_address}')
