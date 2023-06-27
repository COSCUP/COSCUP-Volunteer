''' Track '''
from typing import Any

from toldwords.pretalx import Pretalx, Submission
from toldwords.utils import DATA2023

import setting
from models.trackdb import TrackDB


class Track:
    ''' Track '''

    def __init__(self, pid: str) -> None:
        DATA2023['token'] = setting.PRETALX_API_KEY
        self.pretalx = Pretalx(**DATA2023)
        self.submissions: list[Submission]
        self.pid = pid

    def fetch(self) -> None:
        ''' fetch '''
        self.submissions = []
        for raw in self.pretalx.submissions():
            self.submissions.extend(raw)

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

    def get_raw_subnissions(self) -> None:
        ''' Get submissions data from db '''
        self.submissions = TrackDB().get_raw_submissions(pid=self.pid)

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
            track.fetch()
            track.save_raw_submissions()
            paths.append(f'/schedule/{pid}')
            for name, data in track.tracks().items():
                paths.append(
                    f"/schedule/{pid}/track/{data['code']}/{name}")

        return paths
