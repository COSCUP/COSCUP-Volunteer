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
