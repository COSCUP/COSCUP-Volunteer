''' Index DB '''
from models.budgetdb import BudgetDB
from models.expensedb import ExpenseDB
from models.formdb import FormDB
from models.mailletterdb import MailLetterDB
from models.mattermost_link_db import MattermostLinkDB
from models.mattermostdb import MattermostUsersDB
from models.oauth_db import OAuthDB
from models.projectdb import ProjectDB
from models.senderdb import SenderReceiverDB
from models.teamdb import (TeamDB, TeamMemberChangedDB, TeamMemberTagsDB,
                           TeamPlanDB)
from models.telegram_db import TelegramDB
from models.users_db import UsersDB
from models.usessiondb import USessionDB
from models.waitlistdb import WaitListDB

if __name__ == '__main__':
    BudgetDB().index()
    ExpenseDB().index()
    FormDB().index()
    MailLetterDB().index()
    MattermostLinkDB().index()
    MattermostUsersDB().index()
    OAuthDB().index()
    ProjectDB(pid='').index()
    SenderReceiverDB().index()
    TeamDB(pid='', tid='').index()
    TeamMemberChangedDB().index()
    TeamMemberTagsDB().index()
    TeamPlanDB().index()
    TelegramDB().index()
    USessionDB().index()
    UsersDB().index()
    WaitListDB().index()
