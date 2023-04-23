import datetime
from sqlalchemy.sql import text
import sessionsystem
import tasks
from db import db


def get_all_projects():
    user_id = sessionsystem.session_uid()
    try:
        sql = '''SELECT P.* FROM Projects P, ProjectUsers PU WHERE P.id = PU.pid AND PU.uid = :user_id'''
        res_projects = db.session.execute(
            text(sql), {'user_id': user_id})
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
    except Exception as sql_exception:
        return sql_exception


def new_project(name, description, deadline=None):
    if len(name) > 100:
        return 'Project name is too long'
    if len(description) > 250:
        return 'Project description is too long'
    user_id = sessionsystem.session_uid()
    try:
        # I learned that an INSERT can also return a value if the RETURNING <column> is used
        # This uses it to get the id of the freshly added project to use for adding users to the project
        sql_projects = '''INSERT INTO Projects (name, description, deadline, status) VALUES (:name, :description, :deadline, :status) RETURNING id'''
        res = db.session.execute(
            text(sql_projects), {'name': name, 'description': description, 'deadline': deadline, 'status': 0})
        db.session.commit()
        project_id = res.fetchone()
    except Exception as sql_exception:
        return sql_exception

    # Add creator of project to ProjectUsers
    try:
        sql_projectusers = '''INSERT INTO ProjectUsers (pid, uid, permission, creator) VALUES (:pid, :uid, :permission, :creator)'''
        db.session.execute(text(sql_projectusers), {
                           'pid': int(project_id[0]), 'uid': int(user_id), 'permission': 1, 'creator': True})
        db.session.commit()
    except Exception as sql_exception:
        return sql_exception
    return True


def delete_project(project_id):
    try:
        sql = text('''DELETE FROM Projects WHERE id = :project_id''')
        db.session.execute(sql, {'project_id': project_id})
        db.session.commit()
        del_from_pu = delete_project_from_projectusers(project_id)
        if del_from_pu is True:
            return True
        return del_from_pu
    except Exception as sql_exception:
        return sql_exception


def delete_project_from_projectusers(project_id):
    try:
        sql = text('''DELETE FROM ProjectUsers WHERE pid = :project_id''')
        db.session.execute(sql, {'project_id': project_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def add_user_to_project(username, project_id):
    try:
        sql_user = text('''SELECT id FROM Users WHERE name = :name''')
        res = db.session.execute(sql_user, {'name': username})
        user_id = res.fetchone()
    except Exception as sql_exception:
        return sql_exception
    if user_id:
        in_project = get_user_in_project(project_id, username=username)
        if not in_project:
            try:
                sql_user_to_projectusers = '''INSERT INTO ProjectUsers (pid, uid, permission) VALUES (:project_id, :user_id, :permission)'''
                db.session.execute(text(sql_user_to_projectusers), {
                                   'project_id': int(project_id), 'user_id': user_id[0], 'permission': 0})
                db.session.commit()
            except Exception as sql_exception:
                return sql_exception
            return True
        return 'User already in project'
    return 'User not found'


def get_project(project_id):
    try:
        sql = text('''SELECT * FROM Projects WHERE id = :project_id''')
        res = db.session.execute(sql, {'project_id': project_id})
        project_res = res.fetchone()
        # Formatting the result into a nicer form to use in the page
        project = {'id': project_res[0],
                   'name': project_res[1],
                   'description': project_res[2],
                   'deadline': project_res[3],
                   'status': project_res[4]
                   }
        return project
    except Exception as sql_exception:
        return sql_exception


def get_project_users(project_id):
    try:
        sql = text('''SELECT U.name, U.id, PU.permission, PU.creator FROM Users U, ProjectUsers PU WHERE PU.pid = :project_id AND PU.uid = U.id''')
        res = db.session.execute(sql, {'project_id': project_id})
        users = res.fetchall()
        return users
    except Exception as sql_exception:
        return sql_exception


def get_user_in_project(project_id, username=None, user_id=None):
    if user_id:
        try:
            sql = text('''SELECT PU.uid, PU.permission, PU.creator, U.name FROM ProjectUsers PU, Users U WHERE PU.uid = :user_id AND PU.pid = :project_id AND U.id = PU.uid''')
            res = db.session.execute(
                sql, {'user_id': user_id, 'project_id': project_id})
        except Exception as sql_exception:
            return sql_exception

    elif username:
        try:
            sql = text(
                '''SELECT PU.uid, PU.permission, PU.creator FROM ProjectUsers PU, Users U WHERE U.name = :username AND U.id = PU.uid AND PU.pid = :project_id''')
            res = db.session.execute(
                sql, {'username': username, 'project_id': project_id})
        except Exception as sql_exception:
            return sql_exception

    if user_id or username:
        user = res.fetchone()
        if user:
            return user
    return False


def update_project_name(project_id, name):
    if len(name) > 100:
        return 'Name too long'
    try:
        sql = text('''UPDATE Projects SET name = :name WHERE id = :project_id''')
        db.session.execute(sql, {'name': name, 'project_id': project_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def update_project_description(project_id, description):
    if len(description) > 250:
        return 'Description too long'
    try:
        sql = text(
            '''UPDATE Projects SET description = :description WHERE id = :project_id''')
        db.session.execute(sql, {'description': description, 'id': project_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def update_project_deadline(project_id, deadline):
    try:
        sql = text(
            '''UPDATE Projects SET deadline = :deadline WHERE id = :project_id''')
        db.session.execute(
            sql, {'deadline': deadline, 'project_id': project_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def elevate_user(project_id, user_id):
    try:
        sql = text(
            '''UPDATE ProjectUsers SET permission = 1 WHERE pid = :project_id AND uid = :user_id''')
        db.session.execute(sql, {'project_id': project_id, 'user_id': user_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def demote_user(project_id, user_id):
    user = get_user_in_project(project_id=project_id, user_id=user_id)
    if not user[2]:
        try:
            sql = text(
                '''UPDATE ProjectUsers SET permission = 0 WHERE pid = :project_id AND uid = :user_id''')
            db.session.execute(
                sql, {'project_id': project_id, 'user_id': user_id})
            db.session.commit()
            return True
        except Exception as sql_exception:
            return sql_exception
    return False


def remove_user_from_project(project_id, user_id):
    try:
        sql = text(
            '''DELETE FROM ProjectUsers WHERE pid = :project_id AND uid = :user_id''')
        db.session.execute(sql, {'project_id': project_id, 'user_id': user_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def refresh_projects(projects):
    current_date = datetime.datetime.now().date()
    for project in projects:
        if project['status'] < 2 and ((project['deadline']-current_date).days) < 0:
            update = update_project_status(project['id'], 3)
            if update == Exception:
                return update
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
            except Exception as sql_exception:
                return sql_exception
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
    except Exception as sql_exception:
        return sql_exception
