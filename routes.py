from app import app
import projects
import sessionsystem
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
            # the users parameter is currently being passed in as a blank list until I implement it properly
            project_name = request.form['project_name']
            project_description = request.form['project_description']
            project_deadline = request.form['project_deadline']
            add = projects.new_project(
                project_name, project_description, [], project_deadline)
            if not add:
                return render_template('./error.html', error='Error adding project')
        user_projects = projects.get_all_projects()
        return render_template('./projects.html', projects=user_projects, name=sessionsystem.session_username())
    return redirect('/')


@app.route('/projectview')
def projectview():
    return render_template('./projectview.html')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')
