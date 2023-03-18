''' Main '''
import logging
from time import time
from typing import Awaitable, Callable, Optional

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from api.routers import members, projects, sender, tasks, teams, user
from module.api_token import APIToken

logging.basicConfig(
    filename='/var/log/apps/api.log',
    format='%(asctime)s [%(levelname)-5.5s][%(thread)6.6s] [%(module)s:%(funcName)s#%(lineno)d]: %(message)s',  # pylint: disable=line-too-long
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)

DOC_DESC = '''The more details about how to use this API, please refer to
[API Intro](https://volunteer.coscup.org/docs/dev/api/).'''

TAGS_META = [
    {
        'name': 'user',
        'description': 'More about user self info.',
    },
    {
        'name': 'projects',
        'description': 'List all projects.'
    },
    {
        'name': 'teams',
        'description': 'List all teams.'
    },
    {
        'name': 'tasks',
        'description': 'List all tasks.'
    },
    {
        'name': 'members',
        'description': 'List all members.'
    },
    {
        'name': 'docs',
        'description': 'redirect to docs.',
    },
    {
        'name': 'login',
        'description': 'oauth, login.',
    },
    {
        'name': 'owners',
        'description': 'For platform owners.',
    }
]

app = FastAPI(
    title='Volunteer API.',
    description=DOC_DESC,
    version='2022.10.27',
    openapi_tags=TAGS_META,
    root_path="/api",
    contact={'name': 'Volunteer Team',
             'url': 'https://volunteer.coscup.org/',
             'email': 'volunteer@coscup.org',
             },
    license_info={'name': 'AGPL-3.0',
                  'url': 'https://github.com/COSCUP/COSCUP-Volunteer/blob/master/LICENSE.txt',
                  },
)

app.include_router(members.router)
app.include_router(projects.router)
app.include_router(sender.router)
app.include_router(tasks.router)
app.include_router(teams.router)
app.include_router(user.router)


class Token(BaseModel):
    ''' Token '''
    access_token: str
    token_type: str = Field(default='bearer')


@app.on_event('startup')
async def startup_event() -> None:
    ''' On startup event '''
    logging.info('[API] Startup')


@app.on_event('shutdown')
async def shutdown_event() -> None:
    ''' On shutdown event '''
    logging.info('[API] Shutdown')


@app.middleware('http')
async def request_time(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    ''' Request time '''
    logging.info(
        'request: %s | %s', request.url.path, request.headers)
    start = time()
    response = await call_next(request)
    response.headers['X-Process-Time'] = str(f'{(time() - start):.05}')
    return response


@app.get('/', tags=['docs', ],
         summary='Redirect to API main page',
         response_class=RedirectResponse, status_code=302)
async def index() -> Optional[str]:
    '''Main page '''
    return f'{app.root_path}{app.docs_url}'


@app.post('/token', tags=['login', ],
          summary='Exchange access token',
          response_model=Token)
async def exchange_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()) -> Token | JSONResponse:
    ''' Exchange access token

    Get your **one-time** use `username`, `password` from volenteer
    [personal setting](/setting/api_token) page to exchanging the API access token.

    '''
    verified_uid = APIToken.verify(
        username=form_data.username, password=form_data.password)

    if verified_uid is not None:
        token = APIToken.create_token(uid=verified_uid)
        return Token(access_token=token)

    return JSONResponse(content={}, status_code=status.HTTP_406_NOT_ACCEPTABLE)
