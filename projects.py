from db import db
import sessionsystem
import tasks
from sqlalchemy.sql import text
import datetime


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


def new_project(name, description, deadline=None):
    if len(name) > 100:
        return 'Project name is too long'
    if len(description) > 250:
        return 'Project description is too long'
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
        sql_projectusers = '''INSERT INTO ProjectUsers (pid, uid, permission, creator) VALUES (:pid, :uid, :permission, :creator)'''
        db.session.execute(text(sql_projectusers), {
                           'pid': int(pid[0]), 'uid': int(uid), 'permission': 1, 'creator': True})
        db.session.commit()
    except Exception as e:
        return e
    return True


def delete_project(pid):
    try:
        sql = '''DELETE FROM Projects WHERE id = :pid'''
        db.session.execute(text(sql), {'pid': pid})
        db.session.commit()
        del_from_pu = delete_project_from_projectusers(pid)
        if type(del_from_pu) == bool:
            return True
        else:
            return del_from_pu
    except Exception as e:
        return e


def delete_project_from_projectusers(pid):
    try:
        sql = '''DELETE FROM ProjectUsers WHERE pid = :pid'''
        db.session.execute(text(sql), {'pid': pid})
        db.session.commit()
        return True
    except Exception as e:
        return e


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
        if not in_project:
            try:
                sql_user_to_projectusers = '''INSERT INTO ProjectUsers (pid, uid, permission) VALUES (:pid, :user_id, :permission)'''
                db.session.execute(text(sql_user_to_projectusers), {
                                   'pid': int(project_id), 'user_id': user_id[0], 'permission': 0})
                db.session.commit()
            except Exception as e:
                return e
            return True
        return 'User already in project'
    return 'User not found'


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


def get_project_users(id):
    try:
        sql = '''SELECT U.name, U.id, PU.permission, PU.creator FROM Users U, ProjectUsers PU WHERE PU.pid = :id AND PU.uid = U.id'''
        res = db.session.execute(text(sql), {'id': id})
        users = res.fetchall()
        return users
    except Exception as e:
        return e


def get_user_in_project(pid, username=None, uid=None):
    if uid:
        try:
            sql = '''SELECT PU.uid, PU.permission, PU.creator, U.name FROM ProjectUsers PU, Users U WHERE PU.uid = :uid AND PU.pid = :pid AND U.id = PU.uid'''
            res = db.session.execute(text(sql), {'uid': uid, 'pid': pid})
            user = res.fetchone()
        except Exception as e:
            return e
        if not user:
            return False
        return user
    if username:
        try:
            sql = text(
                '''SELECT PU.uid, PU.permission, PU.creator FROM ProjectUsers PU, Users U WHERE U.name = :username AND U.id = PU.uid AND PU.pid = :pid''')
            res = db.session.execute(
                sql, {'username': username, 'pid': pid})
            user = res.fetchone()
        except Exception as e:
            return e
        if not user:
            return False
        return user


# def get_user_in_project(pid, username: str):
    try:
        sql = text(
            '''SELECT PU.uid, PU.permission, PU.creator FROM ProjectUsers PU, Users U WHERE U.name = :username AND U.id = PU.uid''')
        res = db.session.execute(text(sql), {'username': username, 'pid': pid})
        user = res.fetchone()
    except Exception as e:
        return e
    if not user:
        return False
    return user


def update_project_name(id, name):
    if len(name) > 100:
        return False
    try:
        sql = '''UPDATE Projects SET name = :name WHERE id = :id'''
        db.session.execute(text(sql), {'name': name, 'id': id})
        db.session.commit()
    except Exception as e:
        return e
    return True


def update_project_description(id, description):
    if len(description) > 250:
        return False
    try:
        sql = '''UPDATE Projects SET description = :description WHERE id = :id'''
        db.session.execute(text(sql), {'description': description, 'id': id})
        db.session.commit()
    except Exception as e:
        return e
    return True


def update_project_deadline(id, deadline):
    try:
        sql = '''UPDATE Projects SET deadline = :deadline WHERE id = :id'''
        db.session.execute(text(sql), {'deadline': deadline, 'id': id})
        db.session.commit()
    except Exception as e:
        return e
    return True


def elevate_user(pid, uid):
    try:
        sql = '''UPDATE ProjectUsers SET permission = 1 WHERE pid = :pid AND uid = :uid'''
        db.session.execute(text(sql), {'pid': pid, 'uid': uid})
        db.session.commit()
    except Exception as e:
        return e


def demote_user(pid, uid):
    user = get_user_in_project(pid, uid)
    if not user[2]:
        try:
            sql = '''UPDATE ProjectUsers SET permission = 0 WHERE pid = :pid AND uid = :uid'''
            db.session.execute(text(sql), {'pid': pid, 'uid': uid})
            db.session.commit()
        except Exception as e:
            return e


def remove_user_from_project(pid, uid):
    try:
        sql = '''DELETE FROM ProjectUsers WHERE pid = :pid AND uid = :uid'''
        db.session.execute(text(sql), {'pid': pid, 'uid': uid})
        db.session.commit()
        return True
    except Exception as e:
        return e


def refresh_projects(projects):
    current_date = datetime.datetime.now().date()
    for project in projects:
        if project['status'] < 2 and ((project['deadline']-current_date).days) < 0:
            update = update_project_status(project['id'], 3)
            if update == Exception:
                return update
            else:
                continue
    return True


def refresh_project_status(project_id):
    project_tasks = tasks.get_tasks(project_id)
    for task in project_tasks:
        if task['status'] == -1:
            try:
                sql = text(
                    '''UPDATE Projects SET status = 1 WHERE id = :project_id''')
                db.session.execute(sql, {'project_id': project_id})
                db.session.commit()
                break
            except Exception as e:
                return e
    return True


def update_project_status(project_id, status):
    if status == 2:
        project_tasks = tasks.get_tasks(project_id)
        for task in project_tasks:
            if task['status'] != 1:
                return False
    try:
        sql = text(
            '''UPDATE Projects SET status = :status WHERE id = :project_id''')
        db.session.execute(
            sql, {'status': status, 'project_id': project_id})
        db.session.commit()
        return True
    except Exception as e:
        return e
