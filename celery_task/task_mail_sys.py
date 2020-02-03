from __future__ import absolute_import
from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from celery_task.celery import app

import setting
from module.awsses import AWSSES

logger = get_task_logger(__name__)

@app.task(bind=True, name='mail.sys.test',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.mail.sys.test', exchange='COSCUP-SECRETARY')
def mail_sys_test(sender, **kwargs):
    logger.info('!!! [%s]' % kwargs)
    raise Exception('Test in error and send mail.')


@app.task(bind=True, name='mail.sys.weberror',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.mail.sys.weberror', exchange='COSCUP-SECRETARY')
def mail_sys_weberror(sender, **kwargs):
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)

    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject='[COSCUP-SECRETARY] %s' % kwargs['title'],
        body=kwargs['body'],
    )

    ses.send_raw_email(data=raw_mail)
