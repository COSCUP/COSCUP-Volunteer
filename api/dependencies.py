''' Dependencies '''
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from module.api_token import APIToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
    ''' Get current user '''
    verified_uid = APIToken.verify_token(token=token)

    if verified_uid is not None:
        return {'token': token, 'uid': verified_uid}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate token.',
        headers={"WWW-Authenticate": "Bearer"},
    )
