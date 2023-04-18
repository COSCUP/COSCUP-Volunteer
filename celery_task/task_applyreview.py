''' Task service sync '''
# pylint: disable=unused-argument
from __future__ import absolute_import, unicode_literals

from typing import Any

from celery.utils.log import get_task_logger

from celery_task.celery_main import app
from module.applyreview import ApplyReview

logger = get_task_logger(__name__)


@app.task(bind=True, name='applyreview.submit.one',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cs.applyreview.submit.one', exchange='COSCUP-SECRETARY')
def applyreview_submit_one(sender: Any, **kwargs: str) -> None:
    ''' Apply Review Submit One '''
    pid = kwargs['pid']
    tid = kwargs['tid']
    uid = kwargs['uid']

    result = ApplyReview().submit_review(pid=pid, tid=tid, uid=uid)
    ApplyReview.save_resp_view(pid=pid, tid=tid, uid=uid, resp=result)
