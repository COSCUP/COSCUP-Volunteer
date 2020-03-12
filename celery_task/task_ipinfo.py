from __future__ import absolute_import
from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from celery_task.celery import app
from module.ipinfo import IPInfo
from module.usession import USession

import setting

logger = get_task_logger(__name__)

@app.task(bind=True, name='ipinfo.update.usession',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.ipinfo.update.usession', exchange='COSCUP-SECRETARY')
def ipinfo_update_usession(sender, **kwargs):
    for u in USession.get_no_ipinfo():
        ipinfo_update_usession_one.apply_async(kwargs={'ip': u['header']['X-Real-Ip'], 'sid': u['_id']})

@app.task(bind=True, name='ipinfo.update.usession.one',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.ipinfo.update.usession.one', exchange='COSCUP-SECRETARY')
def ipinfo_update_usession_one(sender, **kwargs):
    logger.info(kwargs)

    r = IPInfo(setting.IPINFO_TOKEN).get(ip=kwargs['ip'])
    USession.update_ipinfo(sid=kwargs['sid'], data=r.json())

@app.task(bind=True, name='session.daily.clean',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.session.daily.clean', exchange='COSCUP-SECRETARY')
def session_daily_clean(sender, **kwargs):
    clean = USession.clean()
    logger.info('matched: %s, modified: %s, raw_result: %s' % (clean.matched_count, clean.modified_count, clean.raw_result))
