''' Sender '''
import csv
import io
from typing import Any

from fastapi import (APIRouter, Depends, File, HTTPException, Path, UploadFile,
                     status)
from pydantic import BaseModel, Field

from api.apistructs.sender import SenderCampaignLists
from api.dependencies import get_current_user
from module.sender import SenderCampaign, SenderReceiver
from module.team import Team
from structs.teams import TeamUsers

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

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs + teamusers.members):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    campaigns = []
    for campaign in SenderCampaign.get_list(pid=pid, tid=tid):
        campaigns.append(campaign)

    return SenderCampaignLists.parse_obj({'datas': campaigns})


class UploadReceiverOutput(BaseModel):
    ''' UploadReceiverOutput '''
    rows: int = Field(description='rows')


async def sender_upload_receiver(
        upload_type: str,
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        cid: str = Path(..., description='campaign id'),
        file: UploadFile = File(
            description='upload csv file', title='Upload csv file.'),
) -> int:
    ''' Upload receiver lists '''

    if not SenderCampaign.get(cid=cid, pid=pid, tid=tid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    content = await file.read()
    csv_rows = list(csv.DictReader(io.StringIO(content.decode('utf8'))))

    saved_rows: int = 0
    if upload_type == 'replace':
        saved_rows = SenderReceiver.replace(pid=pid, cid=cid, datas=csv_rows)
    elif upload_type == 'update':
        saved_rows = SenderReceiver.update(pid=pid, cid=cid, datas=csv_rows)

    return saved_rows


@router.put('/{pid}/{tid}/{cid}/receiver/lists',
            summary='Upload receiver lists (replace)',
            response_model=UploadReceiverOutput,
            responses={
                status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
            response_model_exclude_none=True,
            response_model_by_alias=False,
            )
async def sender_upload_receiver_lists_replace(
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        cid: str = Path(..., description='campaign id'),
        file: UploadFile = File(
            description='upload csv file', title='Upload csv file.'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> UploadReceiverOutput:
    ''' Upload receiver lists (replace) '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs + teamusers.members):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    csv_rows = await sender_upload_receiver(pid=pid, tid=tid, cid=cid,
                                            file=file, upload_type='replace')

    return UploadReceiverOutput.parse_obj({'rows': csv_rows})


@router.patch('/{pid}/{tid}/{cid}/receiver/lists',
              summary='Upload receiver lists (update)',
              response_model=UploadReceiverOutput,
              responses={
                  status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
              response_model_exclude_none=True,
              response_model_by_alias=False,
              )
async def sender_upload_receiver_lists_update(
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        cid: str = Path(..., description='campaign id'),
        file: UploadFile = File(
            description='upload csv file', title='Upload csv file.'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> UploadReceiverOutput:
    ''' Upload receiver lists (update) '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs + teamusers.members):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    csv_rows = await sender_upload_receiver(pid=pid, tid=tid, cid=cid,
                                            file=file, upload_type='update')

    return UploadReceiverOutput.parse_obj({'rows': csv_rows})


@router.delete('/{pid}/{tid}/{cid}/receiver/lists',
               summary='Delete receiver lists (delete)',
               response_model=UploadReceiverOutput,
               responses={
                   status.HTTP_404_NOT_FOUND: {'description': 'Project not found'}},
               response_model_exclude_none=True,
               response_model_by_alias=False,
               )
async def sender_upload_receiver_lists_delete(
        pid: str = Path(..., description='project id'),
        tid: str = Path(..., description='team id'),
        cid: str = Path(..., description='campaign id'),
        current_user: dict[str, Any] = Depends(get_current_user)) -> UploadReceiverOutput:
    ''' Delete receiver lists (delete) '''
    team = Team.get(pid=pid, tid=tid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    teamusers = TeamUsers.parse_obj(team)
    if current_user['uid'] not in (teamusers.owners + teamusers.chiefs + teamusers.members):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return UploadReceiverOutput.parse_obj({
        'rows': SenderReceiver.remove(pid=pid, cid=cid)})
