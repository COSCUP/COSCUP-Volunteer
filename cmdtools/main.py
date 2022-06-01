''' cmd tools '''
import click

from cmdtools import db, dev


@click.group(name='cmd groups')
def main() -> None:
    ''' main cmd '''


main.add_command(cmd=db.main, name='db')
main.add_command(cmd=dev.main, name='dev')

if __name__ == '__main__':
    main()
