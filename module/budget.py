''' Budget '''
import re
from enum import Enum
from typing import Union

import arrow
from pydantic import BaseModel, error_wrappers, validator

from models.budgetdb import BudgetDB
from models.projectdb import ProjectDB
from models.teamdb import TeamDB


class Action(Enum):
    ''' Action '''
    ADD = 'add'
    UPDATE = 'update'


class Currency(Enum):
    ''' Currency '''
    TWD = 'TWD'
    USD = 'USD'


class BudgetImportItem(BaseModel):
    ''' Base Item '''
    # pylint: disable=no-self-argument,no-self-use
    action: Action  # 匯入行為 (add/update)
    bid: str  # 編號（預算表編號）
    tid: str  # 組別（依組別代碼）
    uid: str  # 申請人
    name: str  # 項目名稱
    desc: str  # 項目說明
    total: Union[str, int, float]  # 核定金額
    currency: Currency  # 核定貨幣 (ISO4217)
    paydate: str  # 預定支出日期 (YYYY-MM-DD)
    estimate: str  # 估算方式

    class Config:  # pylint: disable=too-few-public-methods
        ''' Model config '''
        use_enum_values = True

    @validator('total')
    def verify_total(cls, value):
        ''' verify total '''
        value = re.sub('[^0-9.]', '', value)
        if '.' in value:
            return float(value)

        return int(value)

    @validator('paydate')
    def verify_paydate(cls, value, **kwargs):
        ''' verify paydate '''
        if not value:
            return ''

        try:
            date = arrow.get(value)
            return date.format('YYYY-MM-DD')
        except arrow.parser.ParserError:
            kwargs['values']['desc'] = f"預計付款時間：{value}\n{kwargs['values']['desc']}"
            return ''


class Budget:
    ''' Budget class '''

    @staticmethod
    def is_admin(pid, uid):
        ''' check user is admin

        - project owner
        - finance chiefs or members
        - coordinator chiefs

        '''
        if TeamDB(pid=None, tid=None).count_documents({
                'pid': pid,
                'tid': {'$in': ['finance', 'coordinator']},
                '$or': [{'chiefs': uid}, {'members': uid}],
        }):
            return True

        if ProjectDB(pid=None).count_documents({'_id': pid, 'owners': uid}):
            return True

        return False

    @staticmethod
    def add(pid, tid, data):
        ''' Add new data '''
        save = BudgetDB.new(pid=pid, tid=tid, uid=data['uid'])

        for key in save.copy():
            if key in data:
                save[key] = data[key]

        return BudgetDB().add(save)

    @staticmethod
    def edit(pid, data):
        ''' Edit new data '''
        save = {'pid': pid}

        for key in ('name', 'tid', 'uid', 'bid', 'currency', 'total',
                    'desc', 'estimate', 'enabled', 'paydate'):
            if key in data:
                save[key] = data[key]

        if 'enabled' in save:
            save['enabled'] = bool(save['enabled'])

        return BudgetDB().edit(_id=data['_id'], data=save)

    @staticmethod
    def get(buids, pid=None):
        ''' Get by buid '''
        query = {'_id': {'$in': buids}}
        if pid is not None:
            query['pid'] = pid

        return BudgetDB().find(query)

    @staticmethod
    def get_by_pid(pid):
        ''' Get by pid '''
        return BudgetDB().find({'pid': pid}, sort=(('tid', 1), ))

    @staticmethod
    def get_by_tid(pid, tid, only_enable=False):
        ''' Get by pid '''
        if not only_enable:
            return BudgetDB().find({'pid': pid, 'tid': tid})

        return BudgetDB().find({'pid': pid, 'tid': tid, 'enabled': True})

    @staticmethod
    def get_by_bid(pid, bid):
        ''' Get a item according to the specified ``pid`` and ``bid``. '''
        for raw in BudgetDB().find({'pid': pid, 'bid': bid}, {'_id': 1}):
            return raw

    @staticmethod
    def verify_batch_items(items):
        ''' verify the batch items '''
        result = []
        error_result = []
        for (n, raw) in enumerate(items):
            try:
                item = BudgetImportItem.parse_obj(raw)
                result.append(item.dict())
            except error_wrappers.ValidationError as error:
                error_infos = [
                    {'loc': error_info['loc'], 'msg': error_info['msg']}
                    for error_info in error.errors()
                ]
                error_result.append((n, error_infos))

        return result, error_result
