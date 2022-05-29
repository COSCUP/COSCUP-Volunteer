''' cmd '''
from cmd import db

import click


@click.group(name='cmd groups')
def main() -> None:
    ''' main cmd '''


main.add_command(cmd=db.main, name='db')

if __name__ == '__main__':
    main()
