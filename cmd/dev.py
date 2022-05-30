''' dev '''
import click

from models.oauth_db import OAuthDB
from models.usessiondb import USessionDB
from module.oauth import OAuth
from module.users import User
from module.usession import USession


class Token:
    ''' Token data '''
    token: str = 'token.token'
    refresh_token: str = 'token.refresh_token'
    token_uri: str = 'token.token_uri'
    id_token: str = 'token.id_token'
    scopes: list[str] = ['openid', 'https://www.googleapis.com/auth/userinfo.email',
                         'https://www.googleapis.com/auth/userinfo.profile']


@click.group()
def main() -> None:
    ''' For development env '''


@click.command(name='user_add')
def user_add() -> None:
    ''' Create an dev user '''
    user_info = {
        'id': '000000000000000000000',
        'email': 'volunteer@coscup.org',
        'verified_email': True,
        'name': 'Volunteer Dev (testing)',
        'given_name': 'Volunteer',
        'family_name': 'Dev',
        'picture': '',
        'locale': 'en',
    }

    # ----- save oauth info ----- #
    OAuth.add(mail=user_info['email'],
              data=user_info, token=Token())

    for user_oauth in OAuthDB().find():
        click.echo(user_oauth)

    # ----- Check account or create ----- #
    owner = OAuth.owner(mail=user_info['email'])
    if owner:
        user = User(uid=owner).get()
    else:
        user = User.create(mail=user_info['email'])

    click.echo(click.style(
        f"user id: {user['_id']}", fg='green', bold=True))

    user_session = USession.make_new(uid=user['_id'], header={})

    click.echo(click.style(
        f'session id: {user_session.inserted_id}', fg='green', bold=True))

    for user_session in USessionDB().find():
        click.echo(user_session)


main.add_command(cmd=user_add)
