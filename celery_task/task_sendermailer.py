from __future__ import absolute_import
from __future__ import unicode_literals

from celery.utils.log import get_task_logger
from celery_task.celery import app
from markdown import markdown
from module.sender import SenderMailerVolunteer

logger = get_task_logger(__name__)


@app.task(bind=True, name='sender.mailer.volunteer',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.sender.mailer.volunteer', exchange='COSCUP-SECRETARY')
def sender_mailer_volunteer(sender, **kwargs):
    '''campaign_data, team, uids '''
    campaign_data = kwargs['campaign_data']
    team_name = kwargs['team_name']
    user_datas = kwargs['user_datas']

    for user_data in user_datas:
        sender_mailer_volunteer_one.apply_async(
                kwargs={'campaign_data': campaign_data, 'team_name': team_name, 'user_data': user_data})


@app.task(bind=True, name='sender.mailer.volunteer.one',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cs.sender.mailer.volunteer.one', exchange='COSCUP-SECRETARY')
def sender_mailer_volunteer_one(sender, **kwargs):
    campaign_data = kwargs['campaign_data']
    team_name = kwargs['team_name']
    user_data = kwargs['user_data']

    sender_mailer = SenderMailerVolunteer(
            subject=campaign_data['mail']['subject'],
            content={'preheader': campaign_data['mail']['preheader'],
                     'body': markdown(campaign_data['mail']['content']),
                     'send_by': team_name, },
            )

    sender_mailer.send(
        to_list=[{'name': user_data['name'],
                  'mail': user_data['mail']}, ],
        data=user_data,
    )
