''' test module/user '''
import pytest

from models.oauth_db import OAuthDB
from module.users import User


@pytest.fixture(scope='module', params=[None, 'coscup'])
def uid(request):
    ''' uid '''
    return request.param


@pytest.fixture(scope='module', params=[None, 'coscup@coscup.org'])
def mail(request):
    ''' mail '''
    return request.param


class TestUser:  # pylint: disable=too-few-public-methods
    ''' Test User '''

    @staticmethod
    def test_init(uid, mail):  # pylint: disable=redefined-outer-name
        ''' test init '''
        user = User(uid=uid, mail=mail)
        assert user.uid == uid
        assert user.mail == mail

    @staticmethod
    def test_get():
        ''' Test get '''
        user = User(uid='coscup')
        user.get()

    @staticmethod
    def test_create_and_oauth():
        ''' test create user '''
        _mail = 'coscup@coscup.org'
        with pytest.raises(Exception) as error:
            User.create(mail=_mail)

        assert str(error.value) == f'mail: `{_mail}` not in the oauth dbs'

        OAuthDB().add_data(mail=_mail, data={})

        OAuthDB().find_one_and_update(
            {'_id': _mail}, {'$set': {'owner': '00000000'}})

        with pytest.raises(Exception) as error:
            User.create(mail=_mail)

        assert str(error.value) == f'mail:`{_mail}` already bind'

    @staticmethod
    def test_create_success():
        ''' Test create user success '''
        _mail = 'coscup+success@coscup.org'
        OAuthDB().add_data(mail=_mail, data={})
        created_user = User.create(mail=_mail)
        assert created_user['mail'] == _mail

    @staticmethod
    def test_update_profile():
        ''' Test update profile '''
        _mail = 'coscup+updateprofile@coscup.org'
        OAuthDB().add_data(mail=_mail, data={})
        created_user = User.create(mail=_mail)

        data = {'nickname': 'nick coscup'}
        updated_user = User(uid=created_user['_id']).update_profile(data=data)

        assert updated_user['profile']['nickname'] == 'nick coscup'

        real_data = {'name': 'COSCUP'}
        updated_user = User(
            uid=created_user['_id']).update_profile_real(data=real_data)

        assert updated_user['profile_real']['name'] == 'COSCUP'

        suspend_user = User(uid=created_user['_id']).property_suspend()

        assert suspend_user['property']['suspend']
