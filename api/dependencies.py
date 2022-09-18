''' Dependencies '''
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_current_user(token: str = Depends(oauth2_scheme)):
    ''' Get current user '''
    return {'token': token}
