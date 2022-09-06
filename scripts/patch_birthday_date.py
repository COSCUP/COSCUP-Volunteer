''' Patch user profile birthday '''
import arrow

from models.users_db import UsersDB
from models.usessiondb import USessionDB
from module.mc import MC


def patch() -> None:
    ''' do patch '''
    for user in UsersDB().find({'profile_real.birthday': {'$exists': True}}):
        new_date = None
        try:
            new_date = arrow.get(user['profile_real']['birthday']).datetime
        except arrow.parser.ParserError:
            new_date = None

        print(user['_id'], user['profile_real']['birthday'])
        UsersDB().update_one({'_id': user['_id']},
                             {'$set': {'profile_real.birthday': new_date}})

        for session in USessionDB().find({'alive': True, 'uid': user['_id']}):
            MC.get_client().delete(f"sid:{session['_id']}")


def clean_cache() -> None:
    ''' clean cache '''
    for session in USessionDB().find({'alive': True}):
        MC.get_client().delete(f"sid:{session['_id']}")


if __name__ == '__main__':
    patch()
    clean_cache()
