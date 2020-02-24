from __future__ import absolute_import
from __future__ import unicode_literals

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure
from kombu import Exchange, Queue, binding

from module.awsses import AWSSES

import setting

app = Celery(
    main='celery_task',
    broker='amqp://%s' % setting.RABBITMQ,
    include=(
        'celery_task.task_mail_sys',
        'celery_task.task_ipinfo',
        'celery_task.task_service_sync',
    ),
)

app.conf.task_queues = (
    Queue('celery', Exchange('celery', type='direct'), routing_key='celery'),
    Queue('CS_ipinfo', Exchange('COSCUP-SECRETARY', type='topic'), routing_key='cs.ipinfo.#'),
    Queue('CS_mail_member', Exchange('COSCUP-SECRETARY', type='topic'), routing_key='cs.mail.member.#'),
    Queue('CS_mail_sys', Exchange('COSCUP-SECRETARY', type='topic'), routing_key='cs.mail.sys.#'),
    Queue('CS_service_sync', Exchange('COSCUP-SECRETARY', type='topic'), routing_key='cs.servicesync.#'),
)

app.conf.acks_late = True
app.conf.task_ignore_result = True
app.conf.worker_prefetch_multiplier = 2
app.conf.accept_content = ('json', 'pickle')

app.conf.beat_schedule = {
    #'mail-sys-test': {
    #    'task': 'mail.sys.test',
    #    'schedule': crontab(minute='*/5'),
    #    'kwargs': {'msg': 'In testing'},
    #    'options': {
    #        'exchange': 'COSCUP-SECRETARY',
    #        'routing_key': 'cs.mail.sys.test',
    #    },
    #},
    'ipinfo-update-usession': {
        'task': 'ipinfo.update.usession',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.ipinfo.update.session',
        },
    },
    'service_sync.gsuite': {
        'task': 'servicesync.gsuite.memberchange',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.gsuite.memberchange',
        },
    },
    'service_sync.mattermost.users': {
        'task': 'servicesync.mattermost.users',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.mattermost.users',
        },
    },
    'service_sync.mattermost.users': {
        'task': 'servicesync.mattermost.users',
        'schedule': crontab(hour='*/8'),
        'kwargs': {'force': True},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.mattermost.users',
        },
    },
    #'mail.member.waiting': {
    #    'task': 'mail.member.waiting',
    #    'schedule': crontab(minute='*/5'),
    #    'kwargs': {},
    #    'options': {
    #        'exchange': 'COSCUP-SECRETARY',
    #        'routing_key': 'cs.mail.member.waiting',
    #    },
    #},
    #'mail.member.deny': {
    #    'task': 'mail.member.deny',
    #    'schedule': crontab(minute='*/5'),
    #    'kwargs': {},
    #    'options': {
    #        'exchange': 'COSCUP-SECRETARY',
    #        'routing_key': 'cs.mail.member.deny',
    #    },
    #},
    #'mail.member.add': {
    #    'task': 'mail.member.add',
    #    'schedule': crontab(minute='*/5'),
    #    'kwargs': {},
    #    'options': {
    #        'exchange': 'COSCUP-SECRETARY',
    #        'routing_key': 'cs.mail.member.add',
    #    },
    #},
    #'mail.member.del': {
    #    'task': 'mail.member.del',
    #    'schedule': crontab(minute='*/5'),
    #    'kwargs': {},
    #    'options': {
    #        'exchange': 'COSCUP-SECRETARY',
    #        'routing_key': 'cs.mail.member.del',
    #    },
    #},
}

@task_failure.connect
def on_failure(**kwargs):
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)
    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject='[COSCUP-SECRETARY] %s [%s]' % (kwargs['sender'].name, kwargs['sender'].request.id),
        body='kwargs: <pre>%s</pre><br>einfo: <pre>%s</pre><br>request: <pre>%s</pre>' % (
            kwargs['kwargs'], kwargs['einfo'].traceback, kwargs['sender'].request),
    )
    ses.send_raw_email(data=raw_mail)
