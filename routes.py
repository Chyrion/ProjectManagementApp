from app import app
import projects
import sessionsystem
from flask import render_template, request, request, redirect


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        return render_template('./entrypage.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        login = sessionsystem.login(username, password)
        if not login:
            return render_template('./error.html', error='Login error')
        else:
            return redirect('/newproject')
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
            return render_template('/')
    else:
        return render_template('/register.html')


@app.route('/projects', methods=["POST"])
def project_page():
    username = sessionsystem.session_username()
    user_projects = projects.get_projects(username)
    if not user_projects:
        return render_template('./error.html', error='Error fetching user projects')
    return render_template('./projects.html', projects=user_projects, name=username)


@app.route('/projectview')
def projectview():
    return render_template('./projectview.html')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')
