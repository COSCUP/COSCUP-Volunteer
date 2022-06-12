''' MattermostLink '''
from time import time
from typing import Any
from uuid import uuid4

import setting
from models.mattermost_link_db import MattermostLinkDB


class MattermostLink:
    ''' MattermostLink

    Args:
        uid (str): User id.

    '''

    def __init__(self, uid: str) -> None:
        self.uid = uid
        self.raw = MattermostLinkDB().find_one({'_id': uid})

        if not self.raw and uid:
            mml_db = MattermostLinkDB()
            mml_db.insert_one({'_id': uid, 'code': uuid4().hex})
            self.raw = mml_db.find_one({'_id': uid})

    @classmethod
    def verify_save(cls, data: dict[str, Any]) -> bool:
        ''' verify and save data

        Args:
            data (dict): Check the `token`, and verify the user's code.

        Returns:
            `true` or `false`.

        '''
        if 'token' in data and data['token'] == setting.MATTERMOST_SLASH_VOLUNTEER:
            if 'text' in data and data['text']:
                texts = data['text'].split(' ')
                if len(texts) < 2:
                    return False

                cmd, pwd = texts

                if cmd == 'verify':
                    uid, code = pwd.split('.')
                    mml = cls(uid=uid)
                    if mml.raw and code == mml.raw['code']:
                        MattermostLinkDB().find_one_and_update(
                            {'_id': uid}, {'$set': {'data': data, 'create_at': time()}})
                        return True

        return False

    @staticmethod
    def reset(uid: str) -> None:
        ''' Reset the link

        Args:
            uid (str): User id.

        '''
        MattermostLinkDB().delete_one({'_id': uid})
