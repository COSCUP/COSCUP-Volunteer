''' Schedule '''
from flask import Blueprint, render_template
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

from module.mc import MC
from module.track import Track

VIEW_SCHEDULE = Blueprint('schedule', __name__, url_prefix='/schedule')


@VIEW_SCHEDULE.route('/<int:pid>/track/<track_id>/<track_name>')
def show_track(pid: int, track_id: str, track_name: str) -> str | ResponseBase:
    ''' show track '''
    if pid < 2023:
        return Response('', 404)

    submissions = Track(pid=str(pid)).get_submissions_by_track_id(track_id)
    return render_template('schedule_submissions.html',
                           pid=pid,
                           submissions=submissions)


@VIEW_SCHEDULE.route('/<int:pid>')
def index(pid: int) -> str | ResponseBase:
    ''' index '''
    if pid < 2023:
        return Response('', 404)

    mem_cache = MC.get_client()

    track = Track(pid=str(pid))
    if mem_cache.get('schedule'):
        track.get_raw_subnissions()
    else:
        track.fetch()
        track.save_raw_submissions()
        mem_cache.set('schedule', 1, 1800)

    track_name_data = track.tracks()

    # ------ render groups ----- #
    tracks = list(track_name_data.items())
    tracks = sorted(tracks, key=lambda track: track[0])
    tracks_groups = []
    per = round(len(tracks)/3)+1
    for i in range(3):
        tracks_groups.append(tracks[i*per:(i+1)*per])

    track.update_tracks_submissions(tracks=track_name_data)

    return render_template('schedule.html',
                           pid=pid,
                           total_tracks=len(tracks),
                           tracks_groups=tracks_groups)
