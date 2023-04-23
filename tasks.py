from db import db
import sessionsystem
from sqlalchemy.sql import text


def get_tasks(project_id):
    try:
        sql = text(
            '''SELECT * FROM ProjectTasks WHERE pid = :project_id ORDER BY id''')
        res = db.session.execute(sql, {'project_id': project_id})
        tasks = res.fetchall()
        new_tasks = []
        for task in tasks:
            new_task = {
                'id': task[0],
                'pid': task[1],
                'name': task[2],
                'description': task[3],
                'deadline': task[4],
                'status': task[5]
            }
            new_task['users'] = get_task_users(task[0])
            new_tasks.append(new_task)
        return new_tasks
    except Exception as e:
        return e


def get_task(project_id, task_id):
    try:
        sql = text(
            '''SELECT * FROM ProjectTasks WHERE pid = :project_id AND id = :task_id''')
        res = db.session.execute(
            sql, {'project_id': project_id, 'task_id': task_id})
        task = res.fetchone()
        return task
    except Exception as e:
        return e


def get_task_users(task_id):
    try:
        sql = text(
            '''SELECT U.name, U.id, TU.permission, TU.creator FROM Users U, TasksUsers TU WHERE TU.tid = :task_id AND U.id = TU.uid''')
        res = db.session.execute(sql, {'task_id': task_id})
        users = res.fetchall()
        return users
    except Exception as e:
        return e


def get_user_in_task(task_id, user_id):
    try:
        sql = text(
            '''SELECT * FROM TasksUsers WHERE tid = :task_id AND uid = :user_id''')
        res = db.session.execute(sql, {'task_id': task_id, 'user_id': user_id})
        user = res.fetchone()
        if user:
            return user
    except Exception as e:
        return e
    return False


def add_task(project_id, name, description, deadline=None):
    if len(name) > 100:
        return 'Task name is too long'
    if len(description) > 250:
        return 'Task description is too long'
    try:
        if deadline:
            sql = text(
                '''INSERT INTO ProjectTasks (pid, name, description, deadline, status) VALUES (:project_id, :name, :description, :deadline, :status) RETURNING id''')
            res = db.session.execute(sql, {'project_id': project_id, 'name': name,
                                     'description': description, 'deadline': deadline, 'status': -1})
        else:
            sql = text(
                '''INSERT INTO ProjectTasks (pid, name, description, status) VALUES (:project_id, :name, :description, :status) RETURNING id''')
            res = db.session.execute(sql, {'project_id': project_id, 'name': name,
                                     'description': description, 'status': -1})
        db.session.commit()
        task_id = res.fetchone()

        user_id = sessionsystem.session_uid()
        add_user = add_user_to_task(task_id[0], user_id, 1, True)
        if add_user == 1:
            return True
        return add_user
    except Exception as e:
        return e


def add_user_to_task(task_id, user_id, permission, creator):
    try:
        sql = text(
            '''INSERT INTO TasksUsers (tid, uid, permission, creator) VALUES (:task_id, :user_id, :permission, :creator)''')
        db.session.execute(sql, {'task_id': task_id, 'user_id': user_id,
                           'permission': permission, 'creator': creator})
        db.session.commit()
        return True
    except Exception as e:
        return e


def delete_task(project_id, task_id):
    try:
        del_from_tasksusers = delete_task_from_tasksusers(task_id)
        if del_from_tasksusers == True:
            sql = text(
                '''DELETE FROM ProjectTasks WHERE pid = :project_id AND id = :task_id''')
            db.session.execute(
                sql, {'project_id': project_id, 'task_id': task_id})
            db.session.commit()
            return True
        return del_from_tasksusers
    except Exception as e:
        return e


def delete_task_from_tasksusers(task_id):
    try:
        sql = text('''DELETE FROM TasksUsers WHERE tid = :task_id''')
        db.session.execute(sql, {'task_id': task_id})
        db.session.commit()
        return True
    except Exception as e:
        return e


def get_task_status(project_id, task_id):
    try:
        sql = text(
            '''SELECT status FROM ProjectTasks WHERE id = :task_id AND pid = :project_id''')
        res = db.session.execute(
            sql, {'task_id': task_id, 'project_id': project_id})
        status = res.fetchone()
        return status
    except Exception as e:
        return e


def change_task_status(project_id, task_id, user_id):
    user_in = get_user_in_task(task_id, user_id)
    if user_in and user_in != Exception:
        current_status = get_task_status(project_id, task_id)[0]
        new_status = int(current_status) * -1
        try:
            sql = text(
                '''UPDATE ProjectTasks SET status = :new_status WHERE id = :task_id AND pid = :project_id''')
            db.session.execute(
                sql, {'new_status': new_status, 'task_id': task_id, 'project_id': project_id})
            db.session.commit()
        except Exception as e:
            return e
        return True
    elif user_in == Exception:
        return user_in
    return False


def update_task_name(task_id, new_name):
    if len(new_name) > 100:
        return 'Task name too long'
    try:
        sql = text(
            '''UPDATE ProjectTasks SET name = :new_name WHERE id = :task_id''')
        db.session.execute(sql, {'new_name': new_name, 'task_id': task_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def update_task_description(task_id, new_description):
    if len(new_description) > 250:
        return 'Task description too long'
    try:
        sql = text(
            '''UPDATE ProjectTasks SET description = :new_description WHERE id = :task_id''')
        db.session.execute(
            sql, {'new_description': new_description, 'task_id': task_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception


def update_task_deadline(task_id, new_deadline):
    try:
        sql = text(
            '''UPDATE ProjectTasks SET deadline = :new_deadline WHERE id = :task_id''')
        db.session.execute(
            sql, {'new_deadline': new_deadline, 'task_id': task_id})
        db.session.commit()
        return True
    except Exception as sql_exception:
        return sql_exception
