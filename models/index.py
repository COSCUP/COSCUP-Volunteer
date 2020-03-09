from models.formdb import FormDB
from models.mailletterdb import MailLetterDB
from models.mattermost_link_db import MattermostLinkDB
from models.mattermostdb import MattermostUsersDB
from models.oauth_db import OAuthDB
from models.projectdb import ProjectDB
from models.teamdb import TeamDB
from models.teamdb import TeamMemberChangedDB
from models.teamdb import TeamPlanDB
from models.usessiondb import USessionDB
from models.waitlistdb import WaitListDB


if __name__ == '__main__':
    FormDB().index()
    MailLetterDB().index()
    MattermostLinkDB().index()
    MattermostUsersDB().index()
    OAuthDB().index()
    ProjectDB(pid=None).index()
    TeamDB(pid=None, tid=None).index()
    TeamMemberChangedDB().index()
    TeamPlanDB().index()
    USessionDB().index()
    WaitListDB().index()
