''' Track '''
import urllib
from typing import Any

from toldwords.pretalx import Pretalx, Submission, Talk
from toldwords.utils import DATA2023

import setting
from models.trackdb import TalkFavsDB, TrackDB


class Track:
    ''' Track '''

    def __init__(self, pid: str) -> None:
        DATA2023['token'] = setting.PRETALX_API_KEY
        self.pretalx = Pretalx(**DATA2023)
        self.submissions: list[Submission]
        self.talks: list[Talk]
        self.pid = pid

    def fetch(self) -> None:
        ''' fetch '''
        self.talks = []
        for talks in self.pretalx.talks():
            self.talks.extend(talks)

        self.submissions = []
        for submissions in self.pretalx.submissions():
            self.submissions.extend(submissions)

    def tracks(self, lang: str = 'zh-tw') -> dict[str, dict[str, str | list[str]]]:
        ''' tracks '''
        tracks: set[str] = set()
        for data in self.submissions:
            tracks.add(data.track.get(lang, data.track['en']))

        result = TrackDB().build_code(pid=self.pid, tracks=list(tracks), lang=lang)

        return result

    def save_raw_submissions(self) -> None:
        ''' save submissions raw data '''
        TrackDB().save_raw_submissions(pid=self.pid, submissions=self.submissions)

    def save_raw_talks(self) -> None:
        ''' save talks raw data '''
        TrackDB().save_raw_talks(pid=self.pid, talks=self.talks)

    def get_raw_submissions(self) -> None:
        ''' Get submissions data from db '''
        self.submissions = TrackDB().get_raw_submissions(pid=self.pid)

    def get_raw_talks(self) -> None:
        ''' Get talks data from db '''
        self.talks = TrackDB().get_raw_talks(pid=self.pid)

    def update_tracks_submissions(self, tracks: dict[str, dict[str, Any]],
                                  lang: str = 'zh-tw') -> None:
        ''' Update tracks submissions

            track must have `code`, `submissions`.

        '''
        for submission in self.submissions:
            track_name = submission.track.get(lang, submission.track['en'])
            if track_name in tracks:
                if 'submissions' not in tracks[track_name]:
                    tracks[track_name]['submissions'] = []

                tracks[track_name]['submissions'].append(submission.code)

        TrackDB().update_submissions(pid=self.pid, tracks=tracks, lang=lang)

    def get_submissions_by_track_id(self, track_id: str,
                                    state: str = 'confirmed') -> list[Submission]:
        ''' Get Submissions by track_id '''
        return TrackDB().get_submissions_by_track_id(pid=self.pid, track_id=track_id, state=state)

    def get_talks_by_track_id(self, track_id: str) -> list[Talk]:
        ''' Get Talks by track_id '''
        return TrackDB().get_talks_by_track_id(pid=self.pid, track_id=track_id)

    def get_talks_by_talk_ids(self, talk_ids: list[str]) -> list[Talk]:
        ''' Get Talks by talk_ids '''
        return TrackDB().get_talks_by_talk_ids(pid=self.pid, talk_ids=talk_ids)

    def get_talks_by_pid(self) -> list[Talk]:
        ''' Get Talks by pid'''
        return TrackDB().get_talks_by_pid(pid=self.pid)

    def get_talk(self, talk_id: str) -> list[Talk]:
        ''' Get one Talk '''
        return TrackDB().get_talk(pid=self.pid, talk_id=talk_id)

    def save_track_description(self, track_id: str,
                               content: str, lang: str = 'zh-tw') -> None:
        ''' Save track description '''
        TrackDB().save_track_description(pid=self.pid,
                                         track_id=track_id, content=content, lang=lang)

    def get_track_description(self, track_id: str) -> dict[str, str]:
        ''' Get track description '''
        result: dict[str, str] = {}
        for raw in TrackDB().find({'pid': self.pid, 'track_id': track_id}):
            result[raw['lang']] = raw['content']

        return result

    @classmethod
    def sitemap(cls) -> list[str]:
        ''' sitemap '''
        paths: list[str] = []
        for pid in ('2023', ):
            track = cls(pid=pid)
            track.get_raw_submissions()
            paths.append(f'/schedule/{pid}')
            for name, data in track.tracks().items():
                paths.append(
                    f"/schedule/{pid}/track/{data['code']}/{urllib.parse.quote_plus(name)}")
                paths.append(
                    f"/schedule/{pid}/talks/{data['code']}/{urllib.parse.quote_plus(name)}")

            for talk in Track(pid=pid).get_talks_by_pid():
                paths.append(
                    f"/schedule/{pid}/session/{talk.code}")

        return paths


class TalkFavs:
    ''' Talk Favs '''

    def __init__(self, pid: str, uid: str) -> None:
        self.talk_favs_db = TalkFavsDB(pid=pid, uid=uid)

    def get(self) -> list[str]:
        ''' Get talks '''
        return self.talk_favs_db.get()

    def get_share_code(self) -> str:
        ''' Get share code '''
        return self.talk_favs_db.get_share_code()

    def get_by_share_code(self, share_code: str) -> dict[str, Any]:
        ''' Get by share code '''
        return self.talk_favs_db.get_by_share_code(share_code=share_code)

    def add(self, talk_id: str) -> list[str]:
        ''' Add talk '''
        return self.talk_favs_db.add(talk_id=talk_id)

    def delete(self, talk_id: str) -> list[str]:
        ''' Delete talk '''
        return self.talk_favs_db.delete(talk_id=talk_id)

    def sitemap(self) -> list[str]:
        ''' Render sitemap '''
        result: list[str] = []
        for raw in self.talk_favs_db.list():
            result.append(
                f"/schedule/{raw['pid']}/talks/fav/share/{raw['share_code']}")

        return result
