''' Task ipinfo '''
# pylint: disable=unused-argument
from __future__ import absolute_import, unicode_literals

from typing import Any

from celery.utils.log import get_task_logger

import setting
from celery_task.celery_main import app
from module.ipinfo import IPInfo
from module.usession import USession

logger = get_task_logger(__name__)


@app.task(bind=True, name='ipinfo.update.usession',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cs.ipinfo.update.usession', exchange='COSCUP-SECRETARY')
def ipinfo_update_usession(sender: Any) -> None:
    ''' IPInfo update usession '''
    for user in USession.get_no_ipinfo():
        ipinfo_update_usession_one.apply_async(
            kwargs={'ip': user['header']['X-Real-Ip'], 'sid': user['_id']})


@app.task(bind=True, name='ipinfo.update.usession.one',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cs.ipinfo.update.usession.one', exchange='COSCUP-SECRETARY')
def ipinfo_update_usession_one(sender: Any, **kwargs: str) -> None:
    ''' update session ipinfo '''
    logger.info(kwargs)

    resp = IPInfo(setting.IPINFO_TOKEN).get_info(ip_address=kwargs['ip'])
    USession.update_ipinfo(sid=kwargs['sid'], data=resp.json())


@app.task(bind=True, name='session.daily.clean',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cs.session.daily.clean', exchange='COSCUP-SECRETARY')
def session_daily_clean(sender: Any) -> None:
    ''' Daily clean session '''
    clean = USession.clean()
    logger.info('matched: %s, modified: %s, raw_result: %s',
                clean.matched_count, clean.modified_count, clean.raw_result)
