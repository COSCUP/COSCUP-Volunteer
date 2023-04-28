''' Apply Review DB'''
from models.base import DBBase
from structs.teams import TeamApplyReview


class ApplyReviewDB(DBBase):
    ''' Apply Review Collection'''

    def __init__(self) -> None:
        super().__init__('applyreview')

    def index(self) -> None:
        ''' To make collection's index

        Indexs:
            - `pid`, `tid`

        '''
        self.create_index([('pid', 1), ('tid', 1)])

    def save(self, data: TeamApplyReview) -> None:
        ''' Save data

        Args:
            data (TeamApplyReview): the struct of [structs.teams.TeamApplyReview][].

        '''

        self.find_one_and_update(
            {'pid': data.pid, 'tid': data.tid, 'uid': data.uid},
            {'$set': data.dict()},
            upsert=True,
        )
