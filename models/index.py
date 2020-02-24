from models.formdb import FormDB
from models.mattermostdb import MattermostUsersDB
from models.projectdb import ProjectDB
from models.teamdb import TeamDB
from models.teamdb import TeamMemberChangedDB
from models.usessiondb import USessionDB
from models.waitlistdb import WaitListDB


if __name__ == '__main__':
    FormDB().index()
    MattermostUsersDB().index()
    ProjectDB(pid=None).index()
    TeamDB(pid=None, tid=None).index()
    TeamMemberChangedDB().index()
    USessionDB().index()
    WaitListDB().index()
