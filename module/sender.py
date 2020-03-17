import jinja2
from pymongo.collection import ReturnDocument

import setting
from models.senderdb import SenderCampaignDB
from module.awsses import AWSSES


class SenderCampaign(object):
    ''' SenderCampaign class '''

    @staticmethod
    def create(name, pid, tid, uid):
        ''' Create new campaign

        :param str name: campaign name
        :param str pid: pid
        :param str tid: tid
        :param str uid: uid

        '''

        data = SenderCampaignDB.new(name=name.strip(), pid=pid, tid=tid, uid=uid)
        return SenderCampaignDB().save(data)

    @staticmethod
    def get(cid, pid=None, tid=None):
        ''' Get campaign

        :param str cid: cid
        :param str pid: pid
        :param str tid: tid

        '''
        query = {'_id': cid}

        if pid is not None:
            query['created.pid'] = pid

        if tid is not None:
            query['created.tid'] = tid

        return SenderCampaignDB().find_one(query)

    @staticmethod
    def get_list(pid, tid):
        ''' Get list campaign

        :param str pid: pid
        :param str tid: tid

        '''
        return SenderCampaignDB().find({'created.pid': pid, 'created.tid': tid})

    @staticmethod
    def save_mail(cid, subject, content, preheader, layout):
        ''' Save mail data

        :param str cid: cid
        :param str subject: subject
        :param str content: content
        :param str preheader: preheader
        :param str layout: layout

        '''
        return SenderCampaignDB().find_one_and_update(
            {'_id': cid},
            {'$set': {
                'mail.subject': subject,
                'mail.content': content,
                'mail.preheader': preheader,
                'mail.layout': layout,
            }},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def save_receiver(cid, teams, users=None):
        ''' Save receiver

        :param str cid: cid
        :param list teams: teams
        :param list users: users

        '''
        update = {'receiver.teams': teams}
        update['receiver.users'] = users if users else []

        return SenderCampaignDB().find_one_and_update(
            {'_id': cid},
            {'$set': update},
            return_document=ReturnDocument.AFTER,
        )


class SenderMailer(object):
    ''' Sender Mailer

    :param str template_path: template path
    :param str subject: subject
    :param dict source: {'name': str, 'mail': str}

    '''
    def __init__(self, template_path, subject, content, source=None):
        body = jinja2.Environment().from_string(open(template_path, 'r').read()).render(**content)

        self.tpl = jinja2.Environment().from_string(body)
        self.subject = jinja2.Environment().from_string(subject)

        if source is None:
            source = setting.AWS_SES_FROM

        self.awsses = AWSSES(aws_access_key_id=setting.AWS_ID,
                aws_secret_access_key=setting.AWS_KEY, source=source)

    def send(self, to_list, data):
        ''' Send mail

        :param list to_list: [{'name': str, 'mail': str}, ]
        :param dict data: data for render

        '''
        raw_mail = self.awsses.raw_mail(
            to_addresses=to_list,
            subject=self.subject.render(**data),
            body=self.tpl.render(**data),
        )
        return self.awsses.send_raw_email(data=raw_mail)


class SenderMailerVolunteer(SenderMailer):
    ''' Sender using volunteer template '''
    def __init__(self, subject, content, source=None):
        super(SenderMailerVolunteer, self).__init__(
            template_path='/app/templates/mail/sender_base.html',
            subject=subject, content=content, source=source)
