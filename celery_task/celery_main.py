''' Celery '''
from __future__ import absolute_import, unicode_literals

from typing import Any

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure
from kombu import Exchange, Queue

import setting
from module.awsses import AWSSES

app = Celery(
    main='celery_task',
    broker=f'amqp://{setting.RABBITMQ}',
    include=(
        'celery_task.task_applyreview',
        'celery_task.task_expense',
        'celery_task.task_ipinfo',
        'celery_task.task_mail_sys',
        'celery_task.task_sendermailer',
        'celery_task.task_service_sync',
    ),
)

app.conf.task_queues = (
    Queue('celery', Exchange('celery', type='direct'), routing_key='celery'),
    Queue('CS_applyreview', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.applyreview.#'),
    Queue('CS_expense', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.expense.#'),
    Queue('CS_ipinfo', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.ipinfo.#'),
    Queue('CS_mail_member', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.mail.member.#'),
    Queue('CS_mail_sys', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.mail.sys.#'),
    Queue('CS_mail_tasks', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.mail.tasks.#'),
    Queue('CS_sender_mailer', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.sender.mailer.#'),
    Queue('CS_service_sync', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.servicesync.#'),
    Queue('CS_session', Exchange('COSCUP-SECRETARY',
          type='topic'), routing_key='cs.session.#'),
)

app.conf.acks_late = True
app.conf.task_ignore_result = True
app.conf.worker_prefetch_multiplier = 2
app.conf.accept_content = ('json', 'pickle')

app.conf.beat_schedule = {
    # 'mail-sys-test': {
    #    'task': 'mail.sys.test',
    #    'schedule': crontab(minute='*/5'),
    #    'kwargs': {'msg': 'In testing'},
    #    'options': {
    #        'exchange': 'COSCUP-SECRETARY',
    #        'routing_key': 'cs.mail.sys.test',
    #    },
    # },
    'ipinfo-update-usession': {
        'task': 'ipinfo.update.usession',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.ipinfo.update.session',
        },
    },
    'session-daily-clean': {
        'task': 'session.daily.clean',
        'schedule': crontab(hour='21', minute='17'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.session.daily.clean',
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
        'schedule': crontab(minute='12'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.mattermost.users',
        },
    },
    'service_sync.mattermost.users.force': {
        'task': 'servicesync.mattermost.users',
        'schedule': crontab(hour='*/8', minute='17'),
        'kwargs': {'force': True},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.mattermost.users',
        },
    },
    'servicesync.mattermost.projectuserin.channel': {
        'task': 'servicesync.mattermost.projectuserin.channel',
        'schedule': crontab(hour='*/8', minute='24'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.mattermost.projectuserin.channel',
        },
    },
    'servicesync.mattermost.users.position': {
        'task': 'servicesync.mattermost.users.position',
        'schedule': crontab(hour='*/8', minute='27'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.servicesync.mattermost.users.position',
        },
    },
    'mail.member.waiting': {
        'task': 'mail.member.waiting',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.mail.member.waiting',
        },
    },
    'mail.member.deny': {
        'task': 'mail.member.deny',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.mail.member.deny',
        },
    },
    'mail.member.add': {
        'task': 'mail.member.add',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.mail.member.add',
        },
    },
    'mail.member.del': {
        'task': 'mail.member.del',
        'schedule': crontab(minute='*/5'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.mail.member.del',
        },
    },
    'mail.member.welcome': {
        'task': 'mail.member.welcome',
        'schedule': crontab(minute='*/7'),
        'kwargs': {},
        'options': {
            'exchange': 'COSCUP-SECRETARY',
            'routing_key': 'cs.mail.member.welcome',
        },
    },
}


@task_failure.connect
def on_failure(**kwargs: Any) -> None:
    ''' on failure '''
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)
    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject=f"[COSCUP-SECRETARY] {kwargs['sender'].name} [{kwargs['sender'].request.id}]",
        body=f"""kwargs: <pre>{kwargs['kwargs']}</pre><br>
einfo: <pre>{kwargs['einfo'].traceback}</pre><br>
request: <pre>{kwargs['sender'].request}</pre>""",
    )
    ses.send_raw_email(data=raw_mail)
