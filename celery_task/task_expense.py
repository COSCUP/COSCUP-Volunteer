''' Task expense '''
# pylint: disable=unused-argument
from __future__ import absolute_import, unicode_literals

from typing import Any

from celery.utils.log import get_task_logger

import setting
from celery_task.celery_main import app
from models.teamdb import TeamDB
from module.budget import Budget
from module.mattermost_bot import MattermostTools
from module.project import Project
from module.users import User

logger = get_task_logger(__name__)


@app.task(bind=True, name='expense.create',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=2,
          routing_key='cs.expense.create', exchange='COSCUP-SECRETARY')
def expense_create(sender: Any, **kwargs: dict[str, Any]) -> None:  # pylint: disable=too-many-locals
    ''' Expense create '''
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
        uids.update(team['members'])

    project = Project.get(pid=pid)
    if project:
        uids.update(project.owners)

    uids.add(kwargs['expense']['create_by'])

    logger.info(uids)

    users = User.get_info(uids=list(uids))

    mmt = MattermostTools(token=setting.MATTERMOST_BOT_TOKEN,
                          base_url=setting.MATTERMOST_BASEURL)
    for uid in uids:
        mid = mmt.find_possible_mid(uid=uid)
        if mid:
            channel_info = mmt.create_a_direct_message(
                users=(mid, setting.MATTERMOST_BOT_ID)).json()
            message = f"收到 **{users[kwargs['expense']['create_by']]['profile']['badge_name']}**" +\
                f"申請費用 - **[{kwargs['expense']['code']}] / {budget['name']}**" +\
                f"，前往 [管理費用](https://volunteer.coscup.org/expense/{pid})"

            resp = mmt.posts(
                channel_id=channel_info['id'],
                message=message,
            )
            logger.info(resp.json())
