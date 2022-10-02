''' API Structs - Projects '''
from pydantic import BaseModel, Field

from api.apistructs.users import ProjectItem


class ProjectAllOut(BaseModel):
    ''' ProjectAllOut '''
    datas: list[ProjectItem] = Field(
        default=[], description='list of projects')
