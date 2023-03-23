from db import db
import sessionsystem
from sqlalchemy.sql import text


def get_all_projects():
    uid = sessionsystem.session_uid()
    try:
        sql = '''SELECT P.* FROM Projects P, ProjectUsers PU WHERE P.id = PU.pid AND PU.uid = :user_id'''
        res_projects = db.session.execute(
            text(sql), {'user_id': uid})
        projects = res_projects.fetchall()
        return projects
    except Exception as e:
        return e


def new_project(name, description, users, deadline):
    uid = sessionsystem.session_uid()
    pid = 0
    try:
        sql_projects = '''INSERT INTO Projects (name, description, deadline) VALUES (:name, :description, :deadline)'''
        db.session.execute(
            text(sql_projects), {'name': name, 'description': description, 'deadline': deadline})
        db.session.commit()
    except Exception as e:
        return e

    # return True
    try:
        sql_pid = '''SELECT MAX(id) FROM Projects'''
        res = db.session.execute(text(sql_pid))
        pid = res.fetchone()
    except Exception as e:
        return e

    try:
        sql_projectusers = '''INSERT INTO ProjectUsers (pid, uid) VALUES (:pid, :uid)'''
        db.session.execute(text(sql_projectusers), {
                           'pid': int(pid[0]), 'uid': int(uid)})
        db.session.commit()
    except Exception as e:
        return e
    return True


def get_project(name):
    try:
        sql = '''SELECT id, name, description, deadline FROM Projects WHERE name = :name'''
        res = db.session.execute(text(sql), {'name': name})
        project = res.fetchone()
        return project
    except Exception as e:
        return e
