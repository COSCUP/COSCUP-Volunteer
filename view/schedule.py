''' Schedule '''
from flask import (Blueprint, g, jsonify, redirect, render_template, request,
                   session, url_for)
from flask.wrappers import Response
from markdown import markdown
from werkzeug.wrappers import Response as ResponseBase

from celery_task.task_service_sync import service_sync_pretalx_schedule
from module.mc import MC
from module.track import TalkFavs, Track
from module.users import User

VIEW_SCHEDULE = Blueprint('schedule', __name__, url_prefix='/schedule')


@VIEW_SCHEDULE.route('/<int:pid>/talks/all', methods=('GET', 'POST'))
def talks_all(pid: int) -> str | ResponseBase:
    ''' Talks '''
    if pid < 2023:
        return Response('', 404)

    uid = g.get('user', {}).get('account', {}).get('_id')
    talks = Track(pid=str(pid)).get_talks_by_pid()
    talks = sorted(talks, key=lambda talk: talk.slot.room['en'])
    talks = sorted(talks, key=lambda talk: talk.slot.start)

    for talk in talks:
        talk.abstract = markdown(talk.abstract)
        for speaker in talk.speakers:
            if speaker.biography:
                speaker.biography = markdown(speaker.biography)

    if not talks:
        return redirect(f'/schedule/{pid}')

    return render_template('schedule_talks.html',
                           pid=pid,
                           track_id='',
                           all_tracks=True,
                           is_login=bool(uid),
                           title=talks[0].track.get(
                               'zh-tw', talks[0].track['en']),
                           title_en=talks[0].track['en'],
                           share_code='',
                           talks=talks,
                           track_description={})


@VIEW_SCHEDULE.route('/<int:pid>/session/<session_id>', methods=('GET', 'POST'))
def talk_one(pid: int, session_id: str) -> str | ResponseBase:
    ''' Talk one '''
    if pid < 2023:
        return Response('', 404)

    uid = g.get('user', {}).get('account', {}).get('_id')
    talks = Track(pid=str(pid)).get_talk(talk_id=session_id)
    talks = sorted(talks, key=lambda talk: talk.slot.room['en'])
    talks = sorted(talks, key=lambda talk: talk.slot.start)

    for talk in talks:
        talk.abstract = markdown(talk.abstract)
        for speaker in talk.speakers:
            if speaker.biography:
                speaker.biography = markdown(speaker.biography)

    if not talks:
        return redirect('/schedule/2023')

    return render_template('schedule_talks.html',
                           pid=pid,
                           track_id='',
                           one_talk=True,
                           all_tracks=False,
                           is_login=bool(uid),
                           title=talks[0].title,
                           title_en=f'By {talks[0].speakers[0].name}',
                           share_code='',
                           talks=talks,
                           track_description={})


@VIEW_SCHEDULE.route('/<int:pid>/talks/fav/my', methods=('GET', 'POST'))
@VIEW_SCHEDULE.route('/<int:pid>/talks/fav/share/<share_code>', methods=('GET', 'POST'))
def talks_favs_my(pid: int, share_code: str | None = None) -> str | ResponseBase:
    ''' Talks favs '''
    if pid < 2023:
        return Response('', 404)

    uid = g.get('user', {}).get('account', {}).get('_id')
    if not uid and share_code is None:
        session.pop('sid', None)
        session['r'] = request.path
        return redirect(url_for('oauth2callback', _scheme='https', _external=True))

    talk_favs = TalkFavs(pid=str(pid), uid=uid)
    if share_code is None:
        talk_ids = talk_favs.get()
        talks = Track(pid=str(pid)).get_talks_by_talk_ids(talk_ids=talk_ids)
        title = '關注的議程'
        title_en = 'My Favorite Talks'
    else:
        favs_data = talk_favs.get_by_share_code(share_code=share_code)
        user_info = User.get_info(uids=[favs_data['uid'], ])[favs_data['uid']]
        talks = Track(pid=str(pid)).get_talks_by_talk_ids(
            talk_ids=favs_data['talks'])
        title = f"{user_info['profile']['badge_name']} 所關注的議程"
        title_en = f"{user_info['profile']['badge_name']}'s Favorite Talks"

    talks = sorted(talks, key=lambda talk: talk.slot.room['en'])
    talks = sorted(talks, key=lambda talk: talk.slot.start)

    for talk in talks:
        talk.abstract = markdown(talk.abstract)
        for speaker in talk.speakers:
            if speaker.biography:
                speaker.biography = markdown(speaker.biography)

    return render_template('schedule_talks.html',
                           pid=pid,
                           track_id='',
                           is_login=bool(uid),
                           title=title,
                           title_en=title_en,
                           share_code=talk_favs.get_share_code(),
                           talks=talks,
                           track_description={})


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
                           title=talks[0].track.get(
                               'zh-tw', talks[0].track['en']),
                           title_en=talks[0].track['en'],
                           share_code='',
                           talks=talks,
                           track_description=track_description)


@VIEW_SCHEDULE.route('/<int:pid>/track/<track_id>/<track_name>')
def show_track(pid: int, track_id: str, track_name: str) -> str | ResponseBase:
    ''' show track '''
    if pid < 2023:
        return Response('', 404)

    return redirect(f'/schedule/{pid}/talks/{track_id}/{track_name}', code=301)


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
