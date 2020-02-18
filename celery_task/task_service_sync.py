from __future__ import absolute_import
from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from celery_task.celery import app
from models.teamdb import TeamMemberChangedDB
from module.project import Project
from module.service_sync import SyncGSuite
from module.team import Team
from module.users import User
from module.usession import USession

import setting

logger = get_task_logger(__name__)

@app.task(bind=True, name='servicesync.gsuite.memberchange',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.servicesync.gsuite.memberchange', exchange='COSCUP-SECRETARY')
def service_sync_gsuite_memberchange(sender, **kwargs):
    team_member_change_db = TeamMemberChangedDB()
    sync_gsuite = None
    for raw in team_member_change_db.find(
        {'done.gsuite_team': {'$exists': False}},
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
        {'done.gsuite_staff': {'$exists': False}},
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
