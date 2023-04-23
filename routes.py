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
        if not login:
            return render_template('./error.html', error='Login error')
        else:
            return redirect('/projects')
    else:
        return render_template('./login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        if len(username) > 50:
            return render_template('./error.html', error='Username too long')
        if len(password) > 50:
            return render_template('./error.html', error='Password too long')
        reg = sessionsystem.register(username, password)
        if not reg:
            return render_template('./error.html', error='Error registering')
        else:
            return render_template('./entrypage.html')
    else:
        return render_template('/register.html')


@app.route('/logout', methods=['GET'])
def logout():
    sessionsystem.logout()
    return redirect('/')


@app.route('/projects', methods=['GET', 'POST'])
def project_page():
    if sessionsystem.session_uid():
        if request.method == 'POST':
            # new_project(name, description, users, deadline)
            project_name = request.form['project_name']
            project_description = request.form['project_description']
            project_deadline = request.form['project_deadline']
            if not project_deadline:
                project_deadline = datetime.now().date()
            add = projects.new_project(
                name=project_name, description=project_description, deadline=project_deadline)

            # 'add' is a bool (True) if creating the project was successful, otherwise it is an Exception
            if type(add) != bool:
                return render_template('./error.html', error=add)
        user_projects = projects.get_all_projects()
        projects.refresh_projects(user_projects)
        return render_template('./projects.html', projects=user_projects, name=sessionsystem.session_username(), date=datetime.now().date())
    return redirect('/')


@app.route('/projectview/<int:project_id>')
def projectview(project_id):
    user = projects.get_user_in_project(
        pid=project_id, uid=sessionsystem.session_uid())
    if user:
        project = projects.get_project(id=project_id)
        project_tasks = tasks.get_tasks(pid=project_id)

        # I know there is a more compact way to do this, but any attempt I made broke the project page so ????
        tasks_status = 1
        for task in project_tasks:
            if task['status'] == -1:
                tasks_status = -1
                break
        if tasks_status == -1:
            projects.update_project_status(project_id, 1)

        return render_template('./projectview.html', project=project, user=user, date=datetime.now().date(), tasks=project_tasks, tasks_status=tasks_status)
    else:
        return redirect('/')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')


@app.route('/projectedit/<int:id>', methods=['GET', 'POST'])
def projectedit(id):
    if projects.get_user_in_project(pid=id, uid=sessionsystem.session_uid())[1] == 1:
        if request.method == 'GET':
            return render_template('./projectedit.html', id=id)
        else:
            if request.form['project_name']:
                new_name = request.form['project_name']
                projects.update_project_name(id, new_name)
            if request.form['project_description']:
                new_description = request.form['project_description']
                projects.update_project_description(id, new_description)
            if request.form['project_deadline']:
                new_deadline = request.form['project_deadline']
                projects.update_project_deadline(id, new_deadline)
            return redirect(f'/projectview/{id}')
    return redirect('/')


@app.route('/projectedit/<int:project_id>/status/<int:status>', methods=['POST'])
def projectedit_changestatus(project_id, status):
    if projects.get_user_in_project(pid=project_id, uid=sessionsystem.session_uid())[1] == 1:
        update = projects.update_project_status(project_id, status)
        if update == Exception:
            return render_template('./error.html', error=update)
        return redirect(f'/projectview/{project_id}')
    return redirect('/')


@app.route('/projectedit/addtask/<int:id>', methods=['GET', 'POST'])
def projectedit_addtask(id):
    if projects.get_user_in_project(pid=id, uid=sessionsystem.session_uid())[1] == 1:
        if request.method == 'GET':
            return render_template('./addtask.html', id=id)
        elif request.method == 'POST':
            task_name = request.form['task_name']
            task_description = request.form['task_description']
            task_deadline = request.form['task_deadline']
            add = tasks.add_task(
                id, task_name, task_description, task_deadline)
            if type(add) == bool:
                return redirect(f'/projectview/{id}')
            return render_template('./error.html', error=add)
    return redirect('/')


@app.route('/projectedit/<int:project_id>/taskedit/<int:task_id>', methods=['GET', 'POST'])
def projectedit_taskedit(project_id, task_id):
    return redirect('/')


@app.route('/projectedit/<int:project_id>/taskadduser/<int:task_id>', methods=['POST'])
def projectedit_taskadduser(project_id, task_id):
    if projects.get_user_in_project(pid=project_id, uid=sessionsystem.session_uid())[1] == 1:
        username = request.form['username']
        user_to_add_in = projects.get_user_in_project(
            pid=project_id, username=username)

        if user_to_add_in:
            user_in_task = tasks.get_user_in_task(task_id, user_to_add_in[0])
            if not user_in_task:
                add = tasks.add_user_to_task(
                    task_id, user_to_add_in[0], 0, False)
                if add == Exception:
                    return render_template('./error.html', error=add)
                if add == 1:
                    return redirect(f'/projectview/{project_id}')
                return render_template('./error.html', error=add)
            return render_template('./error.html', error='User already in task')
        return render_template('./error.html', error=user_to_add_in)
    return redirect('/')


@app.route('/projectedit/<int:project_id>/taskchangestatus/<int:task_id>', methods=['POST'])
def projectedit_taskchangestatus(project_id, task_id):
    uid = sessionsystem.session_uid()
    if projects.get_user_in_project(pid=project_id, uid=uid)[1] == 1:
        change = tasks.change_task_status(project_id, task_id, uid)
        if change == Exception:
            return render_template('./error.html', error=change)
        if change == False:
            return render_template('./error.html', error='Error with user permissions')
        projects.refresh_project_status(project_id)
        return redirect(f'/projectview/{project_id}')
    return redirect('/')


@app.route('/projectedit/delete/<int:id>', methods=['POST'])
def projectedit_deleteproject(id):
    if projects.get_user_in_project(pid=id, uid=sessionsystem.session_uid())[1] == 1:
        if request.method == 'POST':
            deleted = projects.delete_project(id)
            if type(deleted) != bool:
                return render_template('./error.html', error=deleted)
            else:
                return redirect('/')
        return redirect('/')
    return redirect('/')


@app.route('/projectusers/<int:id>', methods=['GET', 'POST'])
def projectusers(id):
    user_in_project = projects.get_user_in_project(
        pid=id, uid=sessionsystem.session_uid())
    if not user_in_project:
        return redirect('/')
    elif user_in_project[1] == 1:
        users = projects.get_project_users(id)
        if type(users) == Exception:
            return render_template('./error.html', error=users)
        return render_template('./projectusers.html', id=id, users=users)
    return redirect('/')


@app.route('/projectusers/adduser/<int:id>', methods=['GET', 'POST'])
def projectusers_add(id):
    if projects.get_user_in_project(pid=id, uid=sessionsystem.session_uid())[1] == 1:
        if request.method == 'GET':
            return redirect('/')
        else:
            user_to_add = request.form['username']
            add = projects.add_user_to_project(user_to_add, id)
            if type(add) != bool:
                return render_template('./error.html', error=add)
            return redirect(f'/projectusers/{id}')
    return redirect('/')


@app.route('/projectusers/removeuser/<int:pid>&<int:uid>', methods=['GET', 'POST'])
def projectusers_removeuser(pid, uid):
    user_in_project = projects.get_user_in_project(
        pid=pid, uid=sessionsystem.session_uid())
    if not user_in_project:
        return redirect('/')
    elif user_in_project[1] == 1:
        if request.method == 'GET':
            return redirect('/')
        else:
            add = projects.remove_user_from_project(pid=pid, uid=uid)
            if type(add) != bool:
                return render_template('./error.html', error=add)
            return redirect(f'/projectusers/{pid}')
    return redirect('/')


@app.route('/projectusers/elevateuser/<int:project_id>&<int:user_id>', methods=['GET', 'POST'])
def projectusers_elevate(project_id, user_id):
    if request.method == 'POST':
        projects.elevate_user(project_id, user_id)
        return redirect(f'/projectusers/{project_id}')
    return redirect('/')


@app.route('/projectusers/demoteuser/<int:project_id>&<int:user_id>', methods=['GET', 'POST'])
def projectusers_demote(project_id, user_id):
    if request.method == 'POST':
        projects.demote_user(project_id, user_id)
        return redirect(f'/projectusers/{project_id}')
    return redirect('/')
