''' GitlabAPI '''
from requests import Response, Session


class GitlabAPI(Session):
    ''' GitlabAPI '''

    def __init__(self, token: str) -> None:
        super().__init__()
        self.url = 'https://gitlab.com/api/v4'
        self.token = token
        self.headers.update({'Authorization': f'Bearer {self.token}'})

    def get_project(self, project_id: str) -> Response:
        ''' Get Project '''
        return self.get(url=f'{self.url}/projects/{project_id}')

    def post_invite_to_project(self, project_id: str, email: str,
                               access_level: int = 30) -> Response:
        ''' Post invite to project

        access_level 30 => Developer

        https://docs.gitlab.com/ee/api/invitations.html#valid-access-levels
        https://docs.gitlab.com/ee/user/permissions.html#project-members-permissions
        '''
        return self.post(url=f'{self.url}/projects/{project_id}/invitations',
                         data={'email': email, 'access_level': access_level})

    def delete_invite_to_project(self, project_id: str, email: str) -> Response:
        ''' DELETE invite to project '''
        return self.delete(url=f'{self.url}/projects/{project_id}/invitations/{email}')
