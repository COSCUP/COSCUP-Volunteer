from __future__ import print_function

import json

from googleapiclient.discovery import build
from google.oauth2 import service_account


class GSuite(object):
    __slots__ = ('service')

    SCOPES = ('https://www.googleapis.com/auth/admin.directory.user',
              'https://www.googleapis.com/auth/admin.directory.group',
             )

    def __init__(self, credentialfile, with_subject):
        creds = service_account.Credentials.from_service_account_file(
                credentialfile, scopes=self.SCOPES).with_subject(with_subject)

        self.service = build('admin', 'directory_v1', credentials=creds, cache_discovery=False)

    @property
    def print_scopes(self):
        return ','.join(self.SCOPES)

    def users_list(self):
        return self.service.users().list(customer='my_customer', orderBy='email').execute()

    def users_get(self, user_key):
        return self.service.users().get(userKey=user_key).execute()

    # ----- Groups ----- #
    # https://developers.google.com/admin-sdk/directory/v1/reference/groups
    # https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.groups.html
    def groups_get(self, group_key):
        ''' Groups.get '''
        return self.service.groups().get(groupKey=group_key).execute()

    def groups_list(self, page_token=None):
        ''' Groups.list '''
        return self.service.groups().list(customer='my_customer', orderBy='email', pageToken=page_token).execute()

    def groups_list_loop(self, page_token=None):
        ''' Groups.list.loop '''
        groups = self.groups_list(page_token=page_token)
        for group in groups['groups']:
            yield group

        if 'nextPageToken' in groups:
            for group in self.groups_list_loop(page_token=groups['nextPageToken']):
                yield group

    def groups_insert(self, email, description=None, name=None):
        ''' Groups.insert '''
        body = {'email': email}
        if description is not None:
            body['description'] = description

        if name is not None:
            body['name'] = name

        return self.service.groups().insert(body=body).execute()

    # ----- Members ----- #
    # https://developers.google.com/admin-sdk/directory/v1/reference/members
    # https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.members.html
    def members_list(self, group_key, page_token=None):
        ''' members.list '''
        return self.service.members().list(groupKey=group_key, pageToken=page_token).execute()

    def members_list_loop(self, group_key):
        ''' members.list.loop '''
        members = self.members_list(group_key)
        for member in members.get('members', []):
            yield member

        while 'nextPageToken' in members:
            members = self.members_list(group_key, page_token=members['nextPageToken'])
            for member in members.get('members', []):
                yield member

    def members_insert(self, group_key, email, role='MEMBER', delivery_settings='ALL_MAIL'):
        ''' members.insert '''
        body = {'email': email, 'role': role, 'delivery_settings': delivery_settings}
        return self.service.members().insert(groupKey=group_key, body=body).execute()

    def members_has_member(self, group_key, email):
        ''' members.hasMember '''
        try:
            if self.members_get(group_key=group_key, email=email):
                return {'isMember': True}
            return {'isMember': False}
        except:
            return {'isMember': False}

    def members_get(self, group_key, email):
        ''' members.get '''
        return self.service.members().get(groupKey=group_key, memberKey=email).execute()

    def members_delete(self, group_key, email):
        ''' members.delete '''
        return self.service.members().delete(groupKey=group_key, memberKey=email).execute()
