''' Apply review '''
from typing import Any
from toldwords.openai import Message, OpenAIAPI, RespCompletions, Role

import setting
from models.applyreviewdb import ApplyReviewDB
from module.users import User
from module.waitlist import WaitList
from structs.teams import TeamApplyReview, TeamApplyReviewMessage


def review_template(tid: str) -> str:
    ''' review template

    Args:
        tid (str): Team id

    Returns:
        Template content

    '''
    if tid in ('field', ):
        return """
以下是他的自我介紹：\"\"\"%(intro)s\"\"\"
申請加入時所填寫的內容：\"\"\"%(text)s\"\"\"

而在今年的場務工作分組中，分為以下幾組：
 1. 報到組：負責報到相關工作，讓與會者能順利報到、領取大會資料&防疫相關作業，包括但不限於消毒、門禁，保護好大家的健康。
 2. 餐飲組：負責提供零食飲料、工作人員餐點，讓參與的人不要餓著肚子。
 3. 物流組：負責大會所有物資的倉儲、運送、保管等事項。
 4. 機動組：負責場地巡視，並支援其他小組。

請利用以下三點結論：
 1. 是否合適參與志工團隊？
 2. 推薦適合加入哪一工作分組？
 3. 並用關鍵字描繪該志工的優點與缺點。
"""

    return """
以下是他的自我介紹：\"\"\"%(intro)s\"\"\"
申請加入時所填寫的內容：\"\"\"%(text)s\"\"\"

請利用以下三點結論：
 1. 是否合適參與志工團隊？
 2. 並用關鍵字描繪該志工的優點與缺點。
"""


class ApplyReview:
    ''' Apply Review '''
    SYSTEM = """你是一個志工招募人員，接下來將幫忙檢視志工的自我介紹與申請加入時的內容，並協助用簡短評論這位志工的特質，最
後再以關鍵字總結其特質，並都使用繁體中文回覆。"""

    def __init__(self) -> None:
        self.openai_api = OpenAIAPI(**setting.OPENAI_ARGS)

    def submit_review(self, pid: str, tid: str, uid: str) -> RespCompletions:
        ''' Submit review to OpenAI

        Args:
            pid (str): Porject id
            tid (str): Team id
            uid (str): User id

        Returns:
            The struct of `toldwords.openai.RespCompletions`

        '''
        note: str = ''
        for raw in WaitList.get_note(pid=pid, tid=tid, uid=uid):
            note = raw['note']

        intro: str = User.get_info([uid, ])[uid]['profile']['intro']

        resp = self.openai_api.chat_completions(
            n=3,
            messages=[
                Message(role=Role.SYSTEM, content=self.SYSTEM),
                Message(
                    role=Role.USER,
                    content=review_template(tid=tid) % {'intro': intro, 'text': note}),
            ]
        )

        return resp

    @staticmethod
    def save_resp_view(pid: str, tid: str, uid: str, resp: RespCompletions) -> None:
        ''' Save resp view

        Args:
            pid (str): Porject id
            tid (str): Team id
            uid (str): User id
            resp (toldwords.openai.RespCompletions): OpenAI API response

        '''
        data = TeamApplyReview(pid=pid, tid=tid, uid=uid)
        for choice in resp.choices:
            data.messages.append(
                TeamApplyReviewMessage.parse_obj(choice.message)
            )

        ApplyReviewDB().save(data=data)

    @staticmethod
    def get(pid: str, tid: str, uids: list[str]) -> dict[str, Any]:
        ''' Get review result

        Args:
            pid (str): Porject id
            tid (str): Team id
            uids (list): list of user ids

        Returns:
            The same struct with [structs.teams.TeamApplyReview][]

        '''
        result: dict[str, Any] = {}
        for raw in ApplyReviewDB().find({
                'pid': pid, 'tid': tid, 'uid': {'$in': uids}}):
            result[raw['uid']] = raw

        return result
