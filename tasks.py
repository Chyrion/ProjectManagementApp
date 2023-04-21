from db import db
from sqlalchemy.sql import text


def get_tasks(pid):
    try:
        sql = text('''SELECT * FROM ProjectTasks WHERE pid = :pid''')
        res = db.session.execute(sql, {'pid': pid})
        tasks = res.fetchall()
        new_tasks = []
        for task in tasks:
            new_task = {
                'id': task[0],
                'pid': task[1],
                'name': task[2],
                'description': task[3],
                'deadline': task[4]
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
            '''SELECT U.name, U.id FROM Users U, TasksUsers TU WHERE TU.tid = :tid AND U.id = TU.uid''')
        res = db.session.execute(sql, {'tid': tid})
        users = res.fetchall()
        return users
    except Exception as e:
        return e


def add_task(pid, name, description, deadline=None):
    try:
        sql = text(
            '''INSERT INTO ProjectTasks (pid, name, description, deadline) VALUES (:pid, :name, :description, :deadline)''')
        db.session.execute(sql, {'pid': pid, 'name': name,
                           'description': description, 'deadline': deadline})
        db.session.commit()
        return True
    except Exception as e:
        return e
