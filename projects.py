from db import db
import sessionsystem
from sqlalchemy.sql import text


def get_all_projects():
    uid = sessionsystem.session_uid()
    try:
        sql = '''SELECT P.* FROM Projects P, ProjectUsers PU WHERE P.id = PU.pid AND PU.uid = :user_id'''
        res_projects = db.session.execute(
            text(sql), {'user_id': uid})
        projects_res = res_projects.fetchall()
        # Formatting the projects as dicts so they are nicer to handle elsewhere
        projects = []
        for project_raw in projects_res:
            project = {'id': project_raw[0],
                       'name': project_raw[1],
                       'description': project_raw[2],
                       'deadline': project_raw[3],
                       'status': project_raw[4]
                       }
            projects.append(project)
        return projects
    except Exception as e:
        return e


def new_project(name, description, deadline):
    uid = sessionsystem.session_uid()
    try:
        # I learned that an INSERT can also return a value if the RETURNING <column> is used
        # This uses it to get the id of the freshly added project to use for adding users to the project
        sql_projects = '''INSERT INTO Projects (name, description, deadline, status) VALUES (:name, :description, :deadline, :status) RETURNING id'''
        res = db.session.execute(
            text(sql_projects), {'name': name, 'description': description, 'deadline': deadline, 'status': 0})
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
    return True


def add_user_to_project(username, project_id):
    try:
        sql_user = '''SELECT id FROM Users WHERE name = :name'''
        res = db.session.execute(text(sql_user), {'name': username})
        user_id = res.fetchone()
    except Exception as e:
        return e
    if user_id:
        try:
            sql_user_in_project = '''SELECT uid, pid FROM ProjectUsers WHERE uid = :uid AND pid = :pid'''
            res_in_project = db.session.execute(text(sql_user_in_project), {
                                                'uid': user_id[0], 'pid': project_id})
            in_project = res_in_project.fetchone()
        except Exception as e:
            return e
        if in_project:
            try:
                sql_user_to_projectusers = '''INSERT INTO ProjectUsers (pid, uid) VALUES (:pid, :user_id)'''
                db.session.execute(text(sql_user_to_projectusers), {
                                   'pid': int(project_id), 'user_id': user_id[0]})
                db.session.commit()
            except Exception as e:
                return e
            return True
        return False
    return False


def get_project(name):
    try:
        sql = '''SELECT id, name, description, deadline, status FROM Projects WHERE name = :name'''
        res = db.session.execute(text(sql), {'name': name})
        project_res = res.fetchone()
        # Formatting the result into a nicer form to use elsewhere
        project = {'id': project_res[0],
                   'name': project_res[1],
                   'description': project_res[2],
                   'deadline': project_res[3],
                   'status': project_res[4]
                   }
        return project
    except Exception as e:
        return e


def get_project(id):
    try:
        sql = '''SELECT id, name, description, deadline, status FROM Projects WHERE id = :id'''
        res = db.session.execute(text(sql), {'id': id})
        project_res = res.fetchone()
        # Formatting the result into a nicer form to use in the page
        project = {'id': project_res[0],
                   'name': project_res[1],
                   'description': project_res[2],
                   'deadline': project_res[3],
                   'status': project_res[4]
                   }
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
