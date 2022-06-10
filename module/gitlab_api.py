''' GitlabAPI '''
from requests import Response, Session


class GitlabAPI(Session):
    ''' GitlabAPI

    Args:
        token (str): API token.

    Attributes:
        url (str): `https://gitlab.com/api/v4`
        token (str): Specified API token.

    Note:
        The `headers` will update the `Authorization` in `Bearer {self.token}`.
        The API docs: [https://docs.gitlab.com/ee/api/](https://docs.gitlab.com/ee/api/)

    '''

    def __init__(self, token: str) -> None:
        super().__init__()
        self.url = 'https://gitlab.com/api/v4'
        self.token = token
        self.headers.update({'Authorization': f'Bearer {self.token}'})

    def get_project(self, project_id: str) -> Response:
        ''' Get Project

        Args:
            project_id (str): Gitlab's project id.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.get(url=f'{self.url}/projects/{project_id}')

    def post_invite_to_project(self, project_id: str, email: str,
                               access_level: int = 30) -> Response:
        ''' Post invite to project

        Args:
            project_id (str): Gitlab's project id.
            email (str): Email address.
            access_level (int): `30` is for `Developer`.

        References:
            - [#valid-access-levels](https://docs.gitlab.com/ee/\
api/invitations.html#valid-access-levels)
            - [https://docs.gitlab.com/ee/user/permissions.html\
#project-members-permissions](https://docs.gitlab.com/ee/\
user/permissions.html#project-members-permissions)

        '''
        return self.post(url=f'{self.url}/projects/{project_id}/invitations',
                         data={'email': email, 'access_level': access_level})

    def delete_invite_to_project(self, project_id: str, email: str) -> Response:
        ''' DELETE invite to project

        Args:
            project_id (str): Gitlab's project id.
            email (str): Email address.

        Returns:
            Return the [requests.Response][] object.

        '''
        return self.delete(url=f'{self.url}/projects/{project_id}/invitations/{email}')
