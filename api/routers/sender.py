''' Sender '''
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, status

from api.apistructs.sender import SenderCampaignLists
from api.dependencies import get_current_user
from module.sender import SenderCampaign
from module.team import Team

router = APIRouter(
    prefix='/sender',
    tags=['sender'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/{pid}/{tid}',
            summary='List all projects.',
            response_model=SenderCampaignLists,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            response_model_by_alias=False,
            )
async def sender_all(
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> SenderCampaignLists:
    ''' List all sender '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if current_user['uid'] not in (team['owners'] + team['chiefs'] + team['members']):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    campaigns = []
    for campaign in SenderCampaign.get_list(pid=pid, tid=tid):
        campaigns.append(campaign)

    return SenderCampaignLists.parse_obj({'datas': campaigns})
