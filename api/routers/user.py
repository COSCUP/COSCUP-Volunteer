''' User '''
from typing import Any

from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user'],
    responses={status.HTTP_404_NOT_FOUND: {'description': 'Not found'}},
)


@router.get('/me',
            responses={status.HTTP_404_NOT_FOUND: {
                'description': 'Project not found'}})
async def me_info(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    ''' Me '''
    return {'name': 'toomore', 'token': current_user}
