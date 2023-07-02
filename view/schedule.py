''' Schedule '''
from flask import Blueprint, g, redirect, render_template, request, jsonify
from flask.wrappers import Response
from markdown import markdown
from werkzeug.wrappers import Response as ResponseBase

import setting
from celery_task.task_service_sync import service_sync_pretalx_schedule
from module.mc import MC
from module.track import TalkFavs, Track

VIEW_SCHEDULE = Blueprint('schedule', __name__, url_prefix='/schedule')


@VIEW_SCHEDULE.route('/<int:pid>/talks/fav', methods=('GET', 'POST'))
def talks_favs(pid: int) -> str | ResponseBase:
    ''' Talks favs '''
    if pid < 2023:
        return Response('', 404)

    uid = g.get('user', {}).get('account', {}).get('_id')

    if not uid:
        return jsonify({'note': '提醒：需要登入才可以使用加入關注議程功能！'})

    if request.method == 'POST':
        data = request.get_json()

        if data['case'] == 'get':
            favs = TalkFavs(pid=str(pid), uid=uid).get()
            return jsonify({'note': '已匯入關注議程', 'favs': favs})

        if data['case'] == 'add':
            favs = TalkFavs(pid=str(pid), uid=uid).add(talk_id=data['talk_id'])
            return jsonify({'note': '已加入關注', 'favs': favs})

        if data['case'] == 'delete':
            favs = TalkFavs(pid=str(pid), uid=uid).delete(
                talk_id=data['talk_id'])
            return jsonify({'note': '已移除關注', 'favs': favs})

    return jsonify({'note': '????'})


@VIEW_SCHEDULE.route('/<int:pid>/talks/<track_id>/<track_name>')
def show_talks(pid: int, track_id: str, track_name: str) -> str | ResponseBase:
    ''' show talks '''
    if pid < 2023:
        return Response('', 404)

    uid = g.get('user', {}).get('account', {}).get('_id')
    _ = track_name
    talks = Track(pid=str(pid)).get_talks_by_track_id(track_id)
    talks = sorted(talks, key=lambda talk: talk.slot.room['en'])
    talks = sorted(talks, key=lambda talk: talk.slot.start)

    for talk in talks:
        talk.abstract = markdown(talk.abstract)
        for speaker in talk.speakers:
            if speaker.biography:
                speaker.biography = markdown(speaker.biography)

    track_description = Track(
        pid=str(pid)).get_track_description(track_id=track_id)

    if not talks:
        return redirect(f'/schedule/{pid}')

    return render_template('schedule_talks.html',
                           pid=pid,
                           track_id=track_id,
                           is_login=bool(uid),
                           talks=talks,
                           track_description=track_description)


@VIEW_SCHEDULE.route('/<int:pid>/track/<track_id>/<track_name>')
def show_track(pid: int, track_id: str, track_name: str) -> str | ResponseBase:
    ''' show track '''
    if pid < 2023:
        return Response('', 404)

    _ = track_name
    submissions = Track(pid=str(pid)).get_submissions_by_track_id(track_id)
    track_description = Track(
        pid=str(pid)).get_track_description(track_id=track_id)
    return render_template('schedule_submissions.html',
                           pid=pid,
                           submissions=submissions,
                           track_description=track_description,
                           exclude_submissions=setting.EXCLUDE_SUBMISSIONS)


@VIEW_SCHEDULE.route('/<int:pid>')
def index(pid: int) -> str | ResponseBase:
    ''' index '''
    if pid < 2023:
        return Response('', 404)

    mem_cache = MC.get_client()

    track = Track(pid=str(pid))
    track.get_raw_submissions()

    if not mem_cache.get('schedule'):
        service_sync_pretalx_schedule.apply_async(kwargs={'pid': str(pid)})
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
