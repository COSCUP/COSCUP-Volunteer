''' Dependencies '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from module.api_token import APIToken
from module.mc import MC

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    ''' Get current user '''
    serial_no = token.split('|')[0]
    mem_cahce = MC.get_client()

    verified_uid = mem_cahce.get(f'api:{serial_no}')
    if not verified_uid:
        verified_uid = APIToken.verify_token(token=token)

        if verified_uid is not None:
            mem_cahce.set(f'api:{serial_no}', verified_uid, 600)
            return {'token': token, 'uid': verified_uid}
    else:
        return {'token': token, 'uid': verified_uid}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate token.',
        headers={"WWW-Authenticate": "Bearer"},
    )
