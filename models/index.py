from models.projectdb import ProjectDB
from models.teamdb import TeamDB


if __name__ == '__main__':
    ProjectDB(pid=None).index()
    TeamDB(pid=None, tid=None).index()
