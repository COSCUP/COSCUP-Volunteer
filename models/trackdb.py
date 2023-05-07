''' TrackDB '''
from uuid import uuid4

from pymongo import UpdateOne
from toldwords.pretalx import Submission

from models.base import DBBase


class TrackDB(DBBase):
    ''' TrackDB '''

    def __init__(self) -> None:
        super().__init__('tracks')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`
            - `cate`

        '''
        self.create_index([('pid', -1), ('cate', 1)])

    def build_code(self, pid: str, tracks: list[str],
                   lang: str = 'zh-tw') -> dict[str, dict[str, str | list[str]]]:
        ''' Build unit code '''
        result: dict[str, dict[str, str | list[str]]] = {}
        for raw in self.find({'pid': pid, 'cate': 'track', 'name': {'$in': tracks}, 'lang': lang}):
            result[raw['name']] = {'code': raw['code']}

        bulks = []
        for track in tracks:
            if track not in result:
                code = f'{uuid4().node:05x}'[:5]
                result[track] = {'code': code}
                bulks.append(UpdateOne({'pid': pid, 'cate': 'track', 'code': code}, {
                    '$set': {'name': track, 'lang': lang}},
                    upsert=True))

        if bulks:
            self.bulk_write(bulks)

        return result

    def save_raw_submissions(self, pid: str, submissions: list[Submission]) -> None:
        ''' Save submissions raw data '''
        bulks = []
        for submission in submissions:
            bulks.append(UpdateOne({'pid': pid, 'cate': 'raw_sub', 'code': submission.code}, {
                '$set': {'pid': pid, 'code': submission.code, 'raw': submission.dict()}},
                upsert=True))

        if bulks:
            self.bulk_write(bulks)

        self.delete_many(
            {'pid': pid, 'cate': 'raw_sub',
             'code': {'$nin': [submission.code for submission in submissions]}})

    def get_raw_submissions(self, pid: str) -> list[Submission]:
        ''' Get raw submissions '''
        result = []
        for data in self.find({'pid': pid, 'cate': 'raw_sub'}):
            result.append(Submission.parse_obj(data['raw']))

        return result

    def update_submissions(self, pid: str, tracks: dict[str, dict[str, str | list[str]]],
                           lang: str = 'zh-tw') -> None:
        ''' update submissions '''
        bulks = []
        for track in tracks.values():
            bulks.append(UpdateOne({
                'pid': pid, 'cate': 'track', 'code': track['code'], 'lang': lang},
                {'$set': {'submissions': track['submissions']}}
            ))

        if bulks:
            self.bulk_write(bulks)

    def get_submissions_by_track_id(self, pid: str, track_id: str) -> list[Submission]:
        ''' Get submissions by track_id '''

        codes: list[str] = []
        for data in self.find({'pid': pid, 'cate': 'track', 'code': track_id}):
            codes = data['submissions']

        result: list[Submission] = []
        for data in self.find({'pid': pid, 'cate': 'raw_sub', 'code': {'$in': codes}}):
            result.append(Submission.parse_obj(data['raw']))

        return result
