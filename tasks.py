from db import db
import sessionsystem
from sqlalchemy.sql import text


def get_tasks(pid):
    try:
        sql = text('''SELECT * FROM ProjectTasks WHERE pid = :pid ORDER BY id''')
        res = db.session.execute(sql, {'pid': pid})
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
            '''SELECT * FROM ProjectTasks WHERE pid = :pid AND id = :tid''')
        res = db.session.execute(sql, {'pid': project_id, 'tid': task_id})
        task = res.fetchone()
        return task
    except Exception as e:
        return e


def get_task_users(tid):
    try:
        sql = text(
            '''SELECT U.name, U.id, TU.permission, TU.creator FROM Users U, TasksUsers TU WHERE TU.tid = :tid AND U.id = TU.uid''')
        res = db.session.execute(sql, {'tid': tid})
        users = res.fetchall()
        return users
    except Exception as e:
        return e


def get_user_in_task(tid, uid):
    try:
        sql = text('''SELECT * FROM TasksUsers WHERE tid = :tid AND uid = :uid''')
        res = db.session.execute(sql, {'tid': tid, 'uid': uid})
        user = res.fetchone()
    except Exception as e:
        return e
    if not user:
        return False
    return user


def add_task(pid, name, description, deadline=None):
    try:
        if deadline:
            sql = text(
                '''INSERT INTO ProjectTasks (pid, name, description, deadline, status) VALUES (:pid, :name, :description, :deadline, :status) RETURNING id''')
            res = db.session.execute(sql, {'pid': pid, 'name': name,
                                     'description': description, 'deadline': deadline, 'status': -1})
        else:
            sql = text(
                '''INSERT INTO ProjectTasks (pid, name, description, status) VALUES (:pid, :name, :description, :status) RETURNING id''')
            res = db.session.execute(sql, {'pid': pid, 'name': name,
                                     'description': description, 'status': -1})
        db.session.commit()
        task_id = res.fetchone()

        uid = sessionsystem.session_uid()
        add_user = add_user_to_task(task_id[0], uid, 1, True)
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
        return 1
    except Exception as e:
        return e


def delete_task(project_id, task_id):
    try:
        del_from_tasksusers = delete_task_from_tasksusers(task_id)
        if del_from_tasksusers == True:
            sql = text(
                '''DELETE FROM Tasks WHERE pid = :project_id AND tid = :task_id''')
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
