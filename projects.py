from app import app
from db import db
import sessionsystem
from sqlalchemy.sql import text


def get_projects(username):
    user_info = (sessionsystem.session_uid(), sessionsystem.session_username())
    try:
        sql = '''SELECT P.* FROM Projects P, ProjectUsers PU WHERE P.id = PU.pid AND PU.uid =:user_id'''
        projects = db.session.execute(
            text(sql), {'user_id': user_info['uid']}).fetchall()
        return projects
    except:
        return False
