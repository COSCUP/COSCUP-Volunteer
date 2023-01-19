''' Dependencies '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from module.api_token import APIToken
from module.mc import MC
from module.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    ''' Get current user '''
    serial_no = token.split('|')[0]
    mem_cahce = MC.get_client()

    verified_uid = mem_cahce.get(f'api:{serial_no}')
    if not verified_uid:
        verified_uid = APIToken.verify_token(token=token)
        if verified_uid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='No user account.',
                headers={"WWW-Authenticate": "Bearer"},
            )

        mem_cahce.set(f'api:{serial_no}', verified_uid, 600)

    has_suspended: bool | None = mem_cahce.get(f"suspend:{verified_uid}")
    if has_suspended is None:
        has_suspended = User(uid=verified_uid).has_suspended()
        if has_suspended:
            mem_cahce.set(f"suspend:{verified_uid}", True, 300)
        else:
            mem_cahce.set(f"suspend:{verified_uid}", False, 300)

    if has_suspended:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Account has been suspended.',
            headers={"WWW-Authenticate": "Bearer"},
        )

    if verified_uid:
        return {'token': token, 'uid': verified_uid}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate token.',
        headers={"WWW-Authenticate": "Bearer"},
    )
