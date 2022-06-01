''' db '''
import click

from models.index import make_index as make_db_index


@click.group()
def main() -> None:
    ''' db process '''


@click.command(name='make_index')
def make_index() -> None:
    ''' Make Index '''
    click.echo(click.style(
        '[...] Setup the index ...', fg='green', bold=True))
    make_db_index()
    click.echo(click.style(
        '[x] Make indexs for all collections', fg='green', bold=True))


main.add_command(cmd=make_index)
