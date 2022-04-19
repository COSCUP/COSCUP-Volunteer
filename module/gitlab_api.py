''' GitlabAPI '''
# pylint: disable=arguments-renamed,arguments-differ
from requests.sessions import Session


class GitlabAPI(Session):
    ''' GitlabAPI '''

    def __init__(self, token):
        super().__init__()
        self.url = 'https://gitlab.com/api/v4'
        self.token = token
        self.headers.update({'Authorization': f'Bearer {self.token}'})

    def get(self, path, **kwargs):
        ''' GET '''
        return super().get(self.url+path, **kwargs)

    def post(self, path, **kwargs):
        ''' POST '''
        return super().post(self.url+path, **kwargs)

    def delete(self, path, **kwargs):
        ''' DELETE '''
        return super().delete(self.url+path, **kwargs)

    def get_project(self, project_id):
        ''' Get Project '''
        return self.get(f'/projects/{project_id}')

    def post_invite_to_project(self, project_id, email, access_level=30):
        ''' Post invite to project

        access_level 30 => Developer

        https://docs.gitlab.com/ee/api/invitations.html#valid-access-levels
        https://docs.gitlab.com/ee/user/permissions.html#project-members-permissions
        '''
        return self.post(f'/projects/{project_id}/invitations',
                         data={'email': email, 'access_level': access_level})

    def delete_invite_to_project(self, project_id, email):
        ''' DELETE invite to project '''
        return self.delete(f'/projects/{project_id}/invitations/{email}')
