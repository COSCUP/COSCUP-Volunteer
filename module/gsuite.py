''' GSuite '''
from __future__ import print_function

import re
from typing import Any, Generator, Union

from google.oauth2 import service_account  # type: ignore
from googleapiclient import errors  # type: ignore
from googleapiclient.discovery import build  # type:ignore

RE_PICTURE = re.compile(r'(https://.+){1,}=?s([\d]{1,}-c)')


class GSuite:
    ''' GSuite

    Args:
        credentialfile (str): The path to a JSON file.
        with_subject (str): Email address of the Google Workspace admin.

    '''
    __slots__ = ('service', )

    SCOPES = ('https://www.googleapis.com/auth/admin.directory.user',
              'https://www.googleapis.com/auth/admin.directory.group',
              )

    def __init__(self, credentialfile: str, with_subject: str):
        creds = service_account.Credentials.from_service_account_file(
            credentialfile, scopes=self.SCOPES).with_subject(with_subject)

        self.service = build('admin', 'directory_v1',
                             credentials=creds, cache_discovery=False)

    @property
    def print_scopes(self) -> str:
        ''' Print the scopes

        Returns:
            Return an long strings and be chained by `,`.

        '''
        return ','.join(self.SCOPES)

    # ----- Users.list ----- #
    def users_list(self) -> Any:
        ''' Users.list

        Reference:

            - https://googleapis.github.io/google-api-python-client/docs/dyn/\
admin_directory_v1.users.html#list

        '''
        return self.service.users().list(customer='my_customer', orderBy='email').execute()

    # ----- Users.get ----- #
    def users_get(self, user_key: str) -> Any:
        ''' Users.get

        Args:
            user_key (str): mail or google user id.

        Reference:

            - https://googleapis.github.io/google-api-python-client/docs/\
dyn/admin_directory_v1.users.html#get

        '''
        return self.service.users().get(userKey=user_key).execute()

    # ----- Groups ----- #
    def groups_get(self, group_key: str) -> Any:
        ''' Groups.get

        Args:
            group_key (str): mail or group id.

        Reference:

            - https://developers.google.com/admin-sdk/directory/v1/reference/groups
            - https://googleapis.github.io/google-api-python-client/docs/\
dyn/admin_directory_v1.groups.html

        '''
        return self.service.groups().get(groupKey=group_key).execute()

    # ----- Groups.list ----- #
    def groups_list(self, page_token: Union[str, None] = None) -> Any:
        ''' Groups.list

        Args:
            page_token (str): The next page token, it will be supplied in
                              the result if has the next page.

        Reference:

            - https://googleapis.github.io/google-api-python-client/docs/\
dyn/admin_directory_v1.groups.html#list

        '''
        return self.service.groups().list(customer='my_customer',
                                          orderBy='email', pageToken=page_token).execute()

    def groups_list_loop(self, page_token: Union[str, None] = None) ->\
            Generator[dict[str, str], None, None]:
        ''' Groups.list.loop

        Args:
            page_token (str): The next page token, it will be supplied in
                              the result if has the next page.

        '''
        groups = self.groups_list(page_token=page_token)
        for group in groups['groups']:
            yield group

        if 'nextPageToken' in groups:
            for group in self.groups_list_loop(page_token=groups['nextPageToken']):
                yield group

    def groups_insert(self, email: str, description: Union[str, None] = None,
                      name: Union[str, None] = None) -> Any:
        ''' Groups.insert

        Args:
            email (str): Email.
            description (str): Description.
            name (str): Group name.

        '''
        body = {'email': email}
        if description is not None:
            body['description'] = description

        if name is not None:
            body['name'] = name

        return self.service.groups().insert(body=body).execute()

    # ----- Members ----- #
    def members_list(self, group_key: str, page_token: Union[str, None] = None) -> Any:
        ''' members.list

        Args:
            group_key (str): mail or group id.
            page_token (str): The next page token, it will be supplied in
                              the result if has the next page.

        Reference:

            - https://developers.google.com/admin-sdk/directory/v1/reference/members
            - https://googleapis.github.io/google-api-python-client/docs/\
dyn/admin_directory_v1.members.html

        '''
        return self.service.members().list(groupKey=group_key, pageToken=page_token).execute()

    def members_list_loop(self, group_key: str) -> Generator[dict[str, str], None, None]:
        ''' members.list.loop

        Args:
            group_key (str): mail or group id.

        '''
        members = self.members_list(group_key)
        for member in members.get('members', []):
            yield member

        while 'nextPageToken' in members:
            members = self.members_list(
                group_key, page_token=members['nextPageToken'])
            for member in members.get('members', []):
                yield member

    def members_insert(self, group_key: str, email: str,
                       role: str = 'MEMBER', delivery_settings: str = 'ALL_MAIL') -> Any:
        ''' members.insert

        Args:
            group_key (str): mail or group id.
            email (str): Email.
            role (str): `MANAGER`, `MEMBER`, `OWNER`
            delivery_settings (str): `ALL_MAIL`, `DAILY`, `DIGEST`, `DISABLED`, `NONE`.

        Reference:

            - https://developers.google.com/admin-sdk/directory/reference/rest/v1/members

        '''
        body = {'email': email, 'role': role,
                'delivery_settings': delivery_settings}
        return self.service.members().insert(groupKey=group_key, body=body).execute()

    def members_has_member(self, group_key: str, email: str) -> dict[str, bool]:
        ''' members.hasMember

        Args:
            group_key (str): mail or group id.
            email (str): Email.

        '''
        try:
            if self.members_get(group_key=group_key, email=email):
                return {'isMember': True}
            return {'isMember': False}
        except errors.HttpError:
            return {'isMember': False}

    def members_get(self, group_key: str, email: str) -> Any:
        ''' members.get

        Args:
            group_key (str): mail or group id.
            email (str): Email.

        '''
        return self.service.members().get(groupKey=group_key, memberKey=email).execute()

    def members_delete(self, group_key: str, email: str) -> Any:
        ''' members.delete

        Args:
            group_key (str): mail or group id.
            email (str): Email.

        '''
        return self.service.members().delete(groupKey=group_key, memberKey=email).execute()

    @staticmethod
    def size_picture(url: str, size: int = 512) -> str:
        ''' Convert picture size

        Args:
            url (str): The url of the image.
            size (int): Replace the size.

        Returns:
            Return the url of the right size of the image.

        '''
        result = RE_PICTURE.match(url)

        if result:
            _url, _size = result.groups()
            return url.replace(f's{_size}', f's{size}-c')

        return url
