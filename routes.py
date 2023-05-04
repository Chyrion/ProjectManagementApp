from app import app
import projects
import tasks
import sessionsystem
from datetime import datetime, timedelta
from flask import render_template, request, request, redirect


@app.route('/', methods=['POST', 'GET'])
def index():
    if sessionsystem.session_uid():
        return redirect('./projects')
    return render_template('./entrypage.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        login = sessionsystem.login(username, password)
        if isinstance(login, str):
            return render_template('./error.html', error=login)
        return redirect('/projects')
    return render_template('./login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if len(username) > 50:
            return render_template('./error.html', error='Username too long', returnpage='/register')
        if len(password) > 50:
            return render_template('./error.html', error='Password too long', returnpage='/register')
        reg = sessionsystem.register(username, password)
        if isinstance(reg, str):
            return render_template('./error.html', error=reg, returnpage='/register')
        return render_template('./entrypage.html')
    return render_template('/register.html')


@app.route('/logout', methods=['GET'])
def logout():
    sessionsystem.logout()
    return redirect('/')


@app.route('/projects', methods=['GET', 'POST'])
def project_page():
    if sessionsystem.session_uid():
        if request.method == 'POST':
            sessionsystem.check_csrf()
            project_name = request.form['project_name']
            project_description = request.form['project_description']
            project_deadline = request.form['project_deadline']
            if not project_deadline:
                project_deadline = datetime.now().date()

            add = projects.new_project(
                name=project_name, description=project_description, deadline=project_deadline)

            if not isinstance(add, bool):
                return render_template('./error.html', error=add, returnpage='/newproject')
        user_projects = projects.get_all_projects()
        projects.refresh_projects(user_projects)
        return render_template('./projects.html', projects=user_projects, name=sessionsystem.session_username(), date=datetime.now().date())
    return redirect('/')


@app.route('/projectview/<int:project_id>')
def projectview(project_id):
    user = projects.get_user_in_project(
        project_id=project_id, user_id=sessionsystem.session_uid())
    if user:
        project = projects.get_project(project_id=project_id)
        project_tasks = tasks.get_tasks(project_id=project_id)

        # I know there is a more compact way to do this, but any attempt I made broke the project page so ????
        tasks_status = 1
        for task in project_tasks:
            if task['status'] == -1:
                tasks_status = -1
                break
        if tasks_status == -1:
            projects.update_project_status(project_id, 1)

        return render_template('./projectview.html', project=project, user=user, date=datetime.now().date(), tasks=project_tasks, tasks_status=tasks_status)
    return redirect('/')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')


@app.route('/projectedit/<int:project_id>', methods=['GET', 'POST'])
def projectedit(project_id):
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        if request.method == 'POST':
            sessionsystem.check_csrf()
            if request.form['project_name']:
                new_name = request.form['project_name']
                projects.update_project_name(project_id, new_name)
            if request.form['project_description']:
                new_description = request.form['project_description']
                projects.update_project_description(
                    project_id, new_description)
            if request.form['project_deadline']:
                new_deadline = request.form['project_deadline']
                projects.update_project_deadline(project_id, new_deadline)
            return redirect(f'/projectview/{project_id}')
        return render_template('./projectedit.html', id=project_id)
    return redirect('/')


@app.route('/projectedit/<int:project_id>/status/<int:status>', methods=['POST'])
def projectedit_changestatus(project_id, status):
    sessionsystem.check_csrf()
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        update = projects.update_project_status(project_id, status)
        if isinstance(update, Exception):
            return render_template('./error.html', error=update, returnpage=f'/projectview/{project_id}')
        return redirect(f'/projectview/{project_id}')
    return redirect('/')


@app.route('/projectedit/delete/<int:project_id>', methods=['POST'])
def projectedit_deleteproject(project_id):
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        if request.method == 'POST':
            sessionsystem.check_csrf()
            deleted = projects.delete_project(project_id)
            if isinstance(deleted, Exception):
                return render_template('./error.html', error=deleted, returnpage=f'/projectedit/{project_id}')
            return redirect('/')
        return redirect('/')
    return redirect('/')


@app.route('/projectusers/<int:project_id>', methods=['GET', 'POST'])
def projectusers(project_id):
    user_in_project = projects.get_user_in_project(
        project_id=project_id, user_id=sessionsystem.session_uid())
    if not user_in_project:
        return redirect('/')
    elif user_in_project[1] == 1:
        users = projects.get_project_users(project_id)
        if isinstance(users, Exception):
            return render_template('./error.html', error=users, returnpage=f'/projectusers/{project_id}')
        return render_template('./projectusers.html', id=project_id, users=users)
    return redirect('/')


@app.route('/projectusers/adduser/<int:project_id>', methods=['POST'])
def projectusers_add(project_id):
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        if request.method == 'POST':
            sessionsystem.check_csrf()
            user_to_add = request.form['username']
            add = projects.add_user_to_project(user_to_add, project_id)
            if not isinstance(add, bool):
                return render_template('./error.html', error=add, returnpage=f'/projectusers/{project_id}')
            return redirect(f'/projectusers/{project_id}')
    return redirect('/')


@app.route('/projectusers/removeuser/<int:project_id>&<int:user_id>', methods=['POST'])
def projectusers_removeuser(project_id, user_id):
    user_in_project = projects.get_user_in_project(
        project_id=project_id, user_id=sessionsystem.session_uid())
    if not user_in_project:
        return redirect('/')
    elif user_in_project[1] == 1:
        if request.method == 'POST':
            sessionsystem.check_csrf()
            add = projects.remove_user_from_project(
                project_id=project_id, user_id=user_id)
            if not isinstance(add, bool):
                return render_template('./error.html', error=add, returnpage=f'/projectusers/{project_id}')
            return redirect(f'/projectusers/{project_id}')
    return redirect('/')


@app.route('/projectusers/elevateuser/<int:project_id>&<int:user_id>', methods=['POST'])
def projectusers_elevate(project_id, user_id):
    if request.method == 'POST':
        sessionsystem.check_csrf()
        elevate = projects.elevate_user(project_id, user_id)
        if isinstance(elevate, Exception):
            return render_template('./error.html', error=elevate, returnpage=f'/projectusers/{project_id}')
        return redirect(f'/projectusers/{project_id}')
    return redirect('/')


@app.route('/projectusers/demoteuser/<int:project_id>&<int:user_id>', methods=['POST'])
def projectusers_demote(project_id, user_id):
    if request.method == 'POST':
        sessionsystem.check_csrf()
        demote = projects.demote_user(project_id, user_id)
        if isinstance(demote, Exception):
            return render_template('./error.html', error=demote, returnpage=f'/projectusers/{project_id}')
        return redirect(f'/projectusers/{project_id}')
    return redirect('/')


@app.route('/projectedit/addtask/<int:project_id>', methods=['GET', 'POST'])
def projectedit_addtask(project_id):
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        if request.method == 'GET':
            return render_template('./addtask.html', id=project_id)
        elif request.method == 'POST':
            sessionsystem.check_csrf()
            task_name = request.form['task_name']
            task_description = request.form['task_description']
            task_deadline = request.form['task_deadline']
            add = tasks.add_task(
                project_id, task_name, task_description, task_deadline)
            if not isinstance(add, bool):
                return render_template('./error.html', error=add, returnpage=f'/projectedit/addtask/{project_id}')
            projects.refresh_project_status(project_id)
            return redirect(f'/projectview/{project_id}')
    return redirect('/')


@app.route('/projectedit/<int:project_id>/taskedit/<int:task_id>', methods=['GET', 'POST'])
def projectedit_taskedit(project_id, task_id):
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        if request.method == 'GET':
            return render_template('./edittask.html', project_id=project_id, task_id=task_id)
        else:
            sessionsystem.check_csrf()
            if request.form['task_name']:
                new_name = request.form['task_name']
                update_name = tasks.update_task_name(task_id, new_name)
                if not isinstance(update_name, bool):
                    return render_template('./error.html', error=update_name, returnpage=f'/projectedit/{project_id}/taskedit/{task_id}')
            if request.form['task_description']:
                new_description = request.form['task_description']
                update_description = tasks.update_task_description(
                    task_id, new_description)
                if not isinstance(update_name, bool):
                    return render_template('./error.html', error=update_description, returnpage=f'/projectedit/{project_id}/taskedit/{task_id}')
            if request.form['task_deadline']:
                new_deadline = request.form['task_deadline']
                update_deadline = tasks.update_task_deadline(
                    task_id, new_deadline)
                if not isinstance(update_name, bool):
                    return render_template('./error.html', error=update_deadline, returnpage=f'/projectedit/{project_id}/taskedit/{task_id}')
            return redirect(f'/projectview/{project_id}')

    return redirect('/')


@app.route('/projectedit/<int:project_id>/taskadduser/<int:task_id>', methods=['POST'])
def projectedit_taskadduser(project_id, task_id):
    if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
        sessionsystem.check_csrf()
        username = request.form['username']
        user_to_add_in = projects.get_user_in_project(
            project_id=project_id, username=username)

        if user_to_add_in:
            user_in_task = tasks.get_user_in_task(task_id, user_to_add_in[0])
            if not user_in_task:
                add = tasks.add_user_to_task(
                    task_id, user_to_add_in[0], 0, False)
                if isinstance(add, Exception):
                    return render_template('./error.html', error=add, returnpage=f'/projectview/{project_id}')
                return redirect(f'/projectview/{project_id}')
            return render_template('./error.html', error='User already in task', returnpage=f'/projectview/{project_id}')
        return render_template('./error.html', error='User is not in the project', returnpage=f'/projectview/{project_id}')
    return redirect('/')


@app.route('/projectedit/<int:project_id>/taskchangestatus/<int:task_id>', methods=['POST'])
def projectedit_taskchangestatus(project_id, task_id):
    sessionsystem.check_csrf()
    user_id = sessionsystem.session_uid()
    if projects.get_user_in_project(project_id=project_id, user_id=user_id)[1] == 1:
        change = tasks.change_task_status(project_id, task_id, user_id)
        if change == Exception:
            return render_template('./error.html', error=change, returnpage=f'/projectview/{project_id}')
        if change is False:
            return render_template('./error.html', error='Error with user permissions', returnpage=f'/projectview/{project_id}')
        projects.refresh_project_status(project_id)
        return redirect(f'/projectview/{project_id}')
    return redirect('/')


@app.route('/projectedit/<int:project_id>/deletetask/<int:task_id>', methods=['POST'])
def projectedit_deletetask(project_id, task_id):
    if request.method == 'POST':
        sessionsystem.check_csrf()
        if projects.get_user_in_project(project_id=project_id, user_id=sessionsystem.session_uid())[1] == 1:
            delete = tasks.delete_task(project_id, task_id)
            if delete == Exception:
                return render_template('./error.html', error=delete, returnpage=f'/projectedit/{project_id}/taskedit/{task_id}')
            return redirect(f'/projectview/{project_id}')
        return redirect('/')
