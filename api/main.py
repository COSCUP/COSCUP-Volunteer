''' Main '''
from fastapi import FastAPI

app = FastAPI(
    title='Volunteer API.',
    description='API services.',
    version='2022.09.30',
    root_path="/api",
    contact={'name': 'Volunteer Team',
             'url': 'https://volunteer.coscup.org/',
             'email': 'volunteer@coscup.org',
             },
    license_info={'name': 'AGPL-3.0',
                  'url': 'https://github.com/COSCUP/COSCUP-Volunteer/blob/master/LICENSE.txt',
                  },
)


@app.get('/')
async def root() -> dict[str, str]:
    ''' Root page '''
    return {'message': 'Please read the docs.'}


@app.get('/members', tags=['members', ])
async def members(pid: str) -> dict[str, str]:
    ''' Get Project's members '''
    return {'message': f'Get members {pid}'}
