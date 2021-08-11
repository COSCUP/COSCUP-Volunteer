from __future__ import absolute_import
from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from celery_task.celery import app
from models.teamdb import TeamDB
from module.budget import Budget
from module.mattermost_bot import MattermostTools
from module.project import Project
from module.users import User

import setting

logger = get_task_logger(__name__)


@app.task(bind=True, name='expense.create',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=2,
    routing_key='cs.expense.create', exchange='COSCUP-SECRETARY')
def expense_create(sender, **kwargs):
    pid = kwargs['expense']['pid']
    buid = kwargs['expense']['request']['buid']

    budget = None
    for data in Budget.get(buids=[buid, ], pid=pid):
        budget = data

    if not budget:
        return

    uids = set()

    for team in TeamDB(pid=None, tid=None).find({'pid': pid, 'tid': 'finance'}):
        uids.update(team['chiefs'])

    uids.update(Project.get(pid=pid)['owners'])

    logger.info(uids)
    uids = ['6c74e623', ]

    users = User.get_info(uids=list(uids))

    mmt = MattermostTools(token=setting.MATTERMOST_BOT_TOKEN, base_url=setting.MATTERMOST_BASEURL)
    for uid in uids:
        mid = mmt.find_possible_mid(uid=uid)
        if mid:
            channel_info = mmt.create_a_direct_message(users=(mid, setting.MATTERMOST_BOT_ID)).json()

            r = mmt.posts(
                channel_id=channel_info['id'],
                message=u'收到 **%s** 申請費用 - **%s**，前往 [管理費用](https://volunteer.coscup.org/expense/%s)' % (
                        users[uid]['profile']['badge_name'], budget['name'], pid))
            logger.info(r.json())

