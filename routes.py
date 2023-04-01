from app import app
import projects
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
        return render_template('./projects.html', projects=user_projects, name=sessionsystem.session_username(), date=datetime.now().date())
    return redirect('/')


@app.route('/projectview/<int:id>')
def projectview(id):
    if projects.verify_user_in_project(pid=id, uid=sessionsystem.session_uid()):
        project = projects.get_project(id=id)
        return render_template('./projectview.html', project=project, timeleft=timedelta(project['deadline'].day-datetime.now().day))
    else:
        return redirect('/')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')


@app.route('/projectedit/<int:id>', methods=['GET', 'POST'])
def projectedit(id):
    if projects.verify_user_in_project(pid=id, uid=sessionsystem.session_uid()):
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


@app.route('/projectusers/<int:id>', methods=['GET', 'POST'])
def projectusers(id):
    if projects.verify_user_in_project(pid=id, uid=sessionsystem.session_uid()):
        users = projects.get_project_users(id)
        if type(users) == Exception:
            return render_template('./error.html', error=users)
        return render_template('./projectusers.html', id=id, users=users)


@app.route('/projectusers/adduser/<int:id>', methods=['GET', 'POST'])
def projectusers_add(id):
    if projects.verify_user_in_project(pid=id, uid=sessionsystem.session_uid()):
        if request.method == 'GET':
            return redirect('/')
        else:
            user_to_add = request.form['username']
            add = projects.add_user_to_project(user_to_add, id)
            if type(add) != bool:
                return render_template('./error.html', error=add)
            return redirect(f'/projectusers/{id}')
