from pymongo.collection import ReturnDocument

from models.senderdb import SenderCampaignDB


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
