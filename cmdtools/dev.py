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
@click.option('--count', default=10, help='Default create N users.')
def user_add(count) -> None:
    ''' Create an dev user '''

    all_sessions = []
    for serial_no in range(count):
        user_info = {
            'id': f'00000000000000000000{serial_no}',
            'email': f'volunteer+test_{serial_no}@coscup.org',
            'verified_email': True,
            'name': f'Volunteer Dev (testing #{serial_no})',
            'given_name': f'Volunteer #{serial_no}',
            'family_name': 'Dev',
            'picture': 'https://volunteer.coscup.org/img/coscup_volunteer_og.png',
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

        all_sessions.append(user_session)

    click.echo(click.style('\n[!] Next step', bold=True))
    click.echo(click.style(
        ' | Please visit one of these links to setup the cookie/session:', fg='yellow', bold=True))

    for user_session in all_sessions:
        click.echo(click.style(
            f'   -> http://127.0.0.1/dev/cookie?sid={user_session.inserted_id}', fg='green', bold=True))

    click.echo(click.style(
        'Thank you for your contribution!', fg='cyan', bold=True))
    click.echo('')


main.add_command(cmd=user_add)
