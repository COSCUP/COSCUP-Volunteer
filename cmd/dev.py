''' dev '''
import click

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

    # ----- Check account or create ----- #
    owner = OAuth.owner(mail=user_info['email'])
    if owner:
        user = User(uid=owner).get()
    else:
        user = User.create(mail=user_info['email'])

    user_session = USession.make_new(uid=user['_id'], header={})

    click.echo(click.style('\n[!] Next step', bold=True))
    click.echo(click.style(
        ' | Please visit these link to setup the cookie/session:', fg='yellow', bold=True))
    click.echo(click.style(
        f'   -> http://127.0.0.1/dev/cookie?sid={user_session.inserted_id}', fg='green', bold=True))
    click.echo('')
    click.echo(click.style(
        'Thank you for your contribution!', fg='cyan', bold=True))
    click.echo('')


main.add_command(cmd=user_add)
