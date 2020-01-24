from models.projectdb import ProjectDB
from models.teamdb import TeamDB
from models.waitlistdb import WaitListDB


if __name__ == '__main__':
    ProjectDB(pid=None).index()
    TeamDB(pid=None, tid=None).index()
    WaitListDB().index()
