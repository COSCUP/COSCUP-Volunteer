from models.budgetdb import BudgetDB
from models.projectdb import ProjectDB
from models.teamdb import TeamDB


class Budget(object):
    ''' Budget class '''

    @staticmethod
    def is_admin(pid, uid):
        ''' check user is admin

        - project owner
        - finance chiefs
        - coordinator chiefs

        '''
        if TeamDB(pid=None, tid=None).count_documents({
                'pid': pid, 'chiefs': uid, 'tid': {'$in': ['finance', 'coordinator']}}):
            return True

        if ProjectDB(pid=None).count_documents({'_id': pid, 'owners': uid}):
            return True

        return False

    @staticmethod
    def add(pid, tid, data):
        ''' Add new data '''
        save = BudgetDB.new(pid=pid, tid=tid, uid=data['uid'])

        for key in save:
            if key in data:
                save[key] = data[key]

        return BudgetDB().add(save)

    @staticmethod
    def edit(pid, data):
        ''' Edit new data '''
        save = {'pid': data['pid']}

        for key in ('name', 'tid', 'uid', 'bid', 'currency', 'total', 'desc', 'estimate', 'enabled', 'paydate'):
            if key in data:
                save[key] = data[key]

        if 'enabled' in save:
            save['enabled'] = bool(save['enabled'])

        return BudgetDB().edit(_id=data['_id'], data=save)

    @staticmethod
    def get_by_pid(pid):
        ''' Get by pid '''
        return BudgetDB().find({'pid': pid}, sort=(('tid', 1), ))

