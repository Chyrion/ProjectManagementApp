from app import app
from db import db
import projects
import sessionsystem
from flask import Flask, render_template, request, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


@app.route('/', methods=['POST'])
def index():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        login = sessionsystem.login(username, password)
        if not login:
            return render_template('./login.html')
        else:
            return redirect('/newproject')
    return render_template('./login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        reg = sessionsystem.register(username, password)
        if not reg:
            return render_template('./register.html', error=True)
        else:
            return redirect('./login')
    else:
        return render_template('./register.html', error=False)


@app.route('/projects', methods=["POST"])
def project_page():
    username = sessionsystem.get_session()['username']
    user_projects = projects.get_projects(username)
    return render_template('./projects.html', projects=user_projects, name=username)


@app.route('/projectview')
def projectview():
    return render_template('./projectview.html')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')
