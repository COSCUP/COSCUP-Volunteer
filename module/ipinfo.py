''' IPInfo '''
from requests import Response, Session


class IPInfo(Session):
    ''' IPInfo

    Args:
        token (str): IPInfo's API token.

    Attributes:
        url (str): `https://ipinfo.io/`
        token (str): API token.

    Note:
        The `headers` will update the `Authorization` in `Bearer {self.token}`.

    '''

    def __init__(self, token: str):
        super().__init__()
        self.url = 'https://ipinfo.io/'
        self.token = token
        self.headers.update({'Authorization': f'Bearer {self.token}'})

    def get_info(self, ip_address: str) -> Response:
        ''' Get info

        Args:
            ip_address (str): IP address.

        Returns:
            Return the [requests.Response][] object.

        '''
        return super().get(f'{self.url}{ip_address}')
