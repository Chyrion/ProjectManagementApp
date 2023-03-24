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
    try:
        # I learned that an INSERT can also return a value if the RETURNING <column> is used
        # This uses it to get the id of the freshly added project to use for adding users to the project
        sql_projects = '''INSERT INTO Projects (name, description, deadline) VALUES (:name, :description, :deadline) RETURNING id'''
        res = db.session.execute(
            text(sql_projects), {'name': name, 'description': description, 'deadline': deadline})
        db.session.commit()
        pid = res.fetchone()
    except Exception as e:
        return e

    # Add creator of project to ProjectUsers
    try:
        sql_projectusers = '''INSERT INTO ProjectUsers (pid, uid) VALUES (:pid, :uid)'''
        db.session.execute(text(sql_projectusers), {
                           'pid': int(pid[0]), 'uid': int(uid)})
        db.session.commit()
    except Exception as e:
        return e

    # Add other users to ProjectUsers
    # TODO: Fix mass-adding users to a project
    for user in users:
        user = user.strip()
        try:
            sql_user = '''SELECT id FROM Users WHERE name = :name'''
            res = db.session.execute(text(sql_user), {'name': user})
            user_id = res.fetchone()
        except Exception as e:
            return e
        if user_id:
            try:
                sql_user_to_projectusers = '''INSERT INTO ProjectUsers (pid, uid) VALUES (:pid, :user_id)'''
                db.session.execute(text(sql_user_to_projectusers), {
                                   'pid': int(pid[0]), 'user_id': user_id[0]})
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


def get_project(id):
    try:
        sql = '''SELECT id, name, description, deadline FROM Projects WHERE id = :id'''
        res = db.session.execute(text(sql), {'id': id})
        project = res.fetchone()
        return project
    except Exception as e:
        return e


def verify_user_in_project(pid, uid):
    try:
        sql = '''SELECT uid FROM ProjectUsers WHERE uid = :uid AND pid = :pid'''
        res = db.session.execute(text(sql), {'uid': uid, 'pid': pid})
        user_in = res.fetchone()
    except Exception as e:
        return e
    if not user_in:
        return False
    return True
