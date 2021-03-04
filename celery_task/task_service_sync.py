from __future__ import absolute_import
from __future__ import unicode_literals

from time import time

from celery.utils.log import get_task_logger
from celery_task.celery import app
from models.mattermostdb import MattermostUsersDB
from models.teamdb import TeamDB
from models.teamdb import TeamMemberChangedDB
from module.mattermost_bot import MattermostBot
from module.mattermost_bot import MattermostTools
from module.project import Project
from module.service_sync import SyncGSuite
from module.team import Team
from module.users import User
from module.usession import USession

import setting

logger = get_task_logger(__name__)

@app.task(bind=True, name='servicesync.mattermost.users',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.mattermost.users', exchange='COSCUP-SECRETARY')
def service_sync_mattermost_users(sender, **kwargs):
    mmb = MattermostBot(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)

    total_users_count = mmb.get_users_stats().json()['total_users_count']
    db_count = MattermostUsersDB().count_documents({})

    logger.info('total_users_count: %s, db_count: %s' % (total_users_count, db_count))

    if (db_count-3) < total_users_count or 'force' in kwargs:
        mmusers_db = MattermostUsersDB()
        n = 0
        for u in mmb.get_users_loop():
            n += 1
            mmusers_db.save(data=u)

        logger.info('Sync count: %s' % n)


@app.task(bind=True, name='servicesync.gsuite.memberchange',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.gsuite.memberchange', exchange='COSCUP-SECRETARY')
def service_sync_gsuite_memberchange(sender, **kwargs):
    team_member_change_db = TeamMemberChangedDB()
    sync_gsuite = None
    for raw in team_member_change_db.find(
        {'done.gsuite_team': {'$exists': False}, 'case': {'$in': ('add', 'del')}},
        sort=(('create_at', 1), )):
        team = Team.get(raw['pid'], raw['tid'])

        if 'mailling' not in team or not team['mailling']:
            team_member_change_db.find_one_and_update({'_id': raw['_id']}, {'$set': {'done.gsuite_team': True}})
            continue

        if sync_gsuite is None:
            sync_gsuite = SyncGSuite(credentialfile=setting.GSUITE_JSON, with_subject=setting.GSUITE_ADMIN)

        user = User(uid=raw['uid']).get()
        if raw['case'] == 'add':
            sync_gsuite.add_users_into_group(group=team['mailling'], users=(user['mail'], ))
            team_member_change_db.find_one_and_update({'_id': raw['_id']}, {'$set': {'done.gsuite_team': True}})

        elif raw['case'] == 'del':
            sync_gsuite.del_users_from_group(group=team['mailling'], users=(user['mail'], ))
            team_member_change_db.find_one_and_update({'_id': raw['_id']}, {'$set': {'done.gsuite_team': True}})

    for raw in team_member_change_db.find(
        {'done.gsuite_staff': {'$exists': False}, 'case': {'$in': ('add', 'del')}},
        sort=(('create_at', 1), )):
        project = Project.get(raw['pid'])

        if 'mailling_staff' not in project or not project['mailling_staff']:
            team_member_change_db.find_one_and_update({'_id': raw['_id']}, {'$set': {'done.gsuite_staff': True}})
            continue

        if sync_gsuite is None:
            sync_gsuite = SyncGSuite(credentialfile=setting.GSUITE_JSON, with_subject=setting.GSUITE_ADMIN)

        user = User(uid=raw['uid']).get()
        if raw['case'] == 'add':
            sync_gsuite.add_users_into_group(group=project['mailling_staff'], users=(user['mail'], ))
            team_member_change_db.find_one_and_update({'_id': raw['_id']}, {'$set': {'done.gsuite_staff': True}})

        elif raw['case'] == 'del':
            sync_gsuite.del_users_from_group(group=project['mailling_staff'], users=(user['mail'], ))
            team_member_change_db.find_one_and_update({'_id': raw['_id']}, {'$set': {'done.gsuite_staff': True}})


@app.task(bind=True, name='servicesync.gsuite.team_members',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.gsuite.team_members', exchange='COSCUP-SECRETARY')
def service_sync_gsuite_team_members(sender, **kwargs):
    team = Team.get(pid=kwargs['pid'], tid=kwargs['tid'])
    if 'to_team' in kwargs:
        to_team = Team.get(pid=kwargs['to_team'][0], tid=kwargs['to_team'][1])

        if 'mailling' not in to_team or not to_team['mailling']:
            return

        mailling = to_team['mailling']

    else:
        if 'mailling' not in team or not team['mailling']:
            return

        mailling = team['mailling']

    uids = []
    uids.extend(team['chiefs'])
    uids.extend(team['members'])

    users_info = User.get_info(uids=uids)

    sync_gsuite = SyncGSuite(credentialfile=setting.GSUITE_JSON, with_subject=setting.GSUITE_ADMIN)
    sync_gsuite.add_users_into_group(group=mailling, users=[u['oauth']['email'] for u in users_info.values()])

    logger.info('%s %s', mailling, [u['oauth']['email'] for u in users_info.values()])


@app.task(bind=True, name='servicesync.gsuite.team_leader',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.gsuite.team_leader', exchange='COSCUP-SECRETARY')
def service_sync_gsuite_team_leader(sender, **kwargs):
    chiefs = []

    # note: sync all, include `disabled` team
    for team in TeamDB(pid=None, tid=None).find({'pid': kwargs['pid']}):
        chiefs.extend(team['chiefs'])

    users_info = User.get_info(uids=chiefs)

    project = Project.get(pid=kwargs['pid'])
    sync_gsuite = SyncGSuite(credentialfile=setting.GSUITE_JSON, with_subject=setting.GSUITE_ADMIN)
    sync_gsuite.add_users_into_group(group=project['mailling_staff'], users=[u['oauth']['email'] for u in users_info.values()])

    logger.info('%s %s', project['mailling_staff'], [u['oauth']['email'] for u in users_info.values()])

@app.task(bind=True, name='servicesync.mattermost.invite',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.mattermost.invite', exchange='COSCUP-SECRETARY')
def service_sync_mattermost_invite(sender, **kwargs):
    mmb = MattermostBot(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)

    users_info = User.get_info(uids=kwargs['uids'])
    r = mmb.post_invite_by_email(
            team_id=setting.MATTERMOST_TEAM_ID,
            emails=[users_info[uid]['oauth']['email'] for uid in users_info])
    logger.info(r.json())

@app.task(bind=True, name='servicesync.mattermost.add.channel',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.mattermost.add.channel', exchange='COSCUP-SECRETARY')
def service_sync_mattermost_add_channel(sender, **kwargs):
    project = Project.get(pid=kwargs['pid'])
    if not ('mattermost_ch_id' in project and project['mattermost_ch_id']):
        return

    mmt = MattermostTools(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
    for uid in kwargs['uids']:
        mid = mmt.find_possible_mid(uid=uid)
        if mid:
            r = mmt.post_user_to_channel(channel_id=project['mattermost_ch_id'], uid=mid)
            logger.info(r.json())

@app.task(bind=True, name='servicesync.mattermost.projectuserin.channel',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=2,
    routing_key='cs.servicesync.mattermost.projectuserin.channel', exchange='COSCUP-SECRETARY')
def service_sync_mattermost_projectuserin_channel(sender, **kwargs):
    pids = {}
    for project in Project.all():
        if project['action_date'] >= time() and 'mattermost_ch_id' in project and project['mattermost_ch_id']:
            pids[project['_id']] = project['mattermost_ch_id']

    if not pids:
        return

    mmt = MattermostTools(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
    for pid in pids:
        uids = set()
        for team in Team.list_by_pid(pid=pid):
            uids.update(team['chiefs'])
            uids.update(team['members'])

        for uid in uids:
            mid = mmt.find_possible_mid(uid=uid)
            if mid:
                r = mmt.post_user_to_channel(channel_id=pids[pid], uid=mid)
                logger.info(r.json())

@app.task(bind=True, name='servicesync.mattermost.users.position',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=2,
    routing_key='cs.servicesync.mattermost.users.position', exchange='COSCUP-SECRETARY')
def service_sync_mattermost_users_position(sender, **kwargs):
    pids = []
    for project in Project.all():
        if project['action_date'] >= time():
            pids.append(project['_id'])

    if not pids:
        return

    for pid in pids:
        users = {}
        for team in Team.list_by_pid(pid=pid):
            team_name = team['name'].split('-')[0].strip()

            for chief in team['chiefs']:
                if chief not in users:
                    users[chief] = []

                if team['tid'] == 'coordinator':
                    users[chief].append('🌟總召')
                else:
                    users[chief].append('⭐️組長@%s' % team_name)

            team['members'] = set(team['members']) - set(team['chiefs'])
            for member in team['members']:
                if member not in users:
                    users[member] = []

                users[member].append('%s(組員)' % team_name)

        mmt = MattermostTools(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
        mmb = MattermostBot(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)

        for uid in users:
            mid = mmt.find_possible_mid(uid=uid)
            if not mid:
                continue

            position = [pid, ]
            position.extend(users[uid])
            position.append('[%s]' % uid)
            mmb.put_users_patch(uid=mid, position=' '.join(position))

