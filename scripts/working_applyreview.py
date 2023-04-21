''' Wording Apply Review '''
from module.applyreview import ApplyReview
from module.team import Team
from module.waitlist import WaitList
from celery_task.task_applyreview import applyreview_submit_one


def run_process_one(pid: str, tid: str, uid: str):
    ''' Run one '''
    result = ApplyReview().submit_review(pid=pid, tid=tid, uid=uid)
    ApplyReview.save_resp_view(pid=pid, tid=tid, uid=uid, resp=result)


def run_process(pid: str):
    ''' Run '''
    for team in Team.list_by_pid(pid=pid):
        waiting_data = WaitList.list_by_team(pid=pid, tid=team.id)
        if waiting_data is None:
            break

        for user in waiting_data:
            applyreview_submit_one.apply_async(kwargs={
                'pid': pid, 'tid': team.id, 'uid': user['uid'],
            })


if __name__ == '__main__':
    # run_process('2023')
    pass
