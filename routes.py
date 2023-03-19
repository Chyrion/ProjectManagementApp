from app import app
from db import db
from flask import Flask, render_template, request, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


@app.route('/')
def index():
    return render_template('./login.html')


@app.route('/projects', methods=["POST"])
def project_page():
    username = request.form['username']
    try:
        sql_user_id = """SELECT id, name FROM Users WHERE name = :name"""
        res_user_id = db.session.execute(text(sql_user_id), {'name': username})
        user = res_user_id.fetchone()
    except:
        pass

    sql_projects = text(
        """SELECT P.* FROM Projects P, ProjectUsers PU WHERE P.id = PU.pid AND PU.uid =:user_id """)
    projects = db.session.execute(
        sql_projects, {'user_id': user[0]}).fetchall()
    print(user)

    return render_template('./projects.html', projects=projects, name=user[1])


@app.route('/projectview')
def projectview():
    return render_template('./projectview.html')


@app.route('/newproject')
def newproject():
    return render_template('./newproject.html')
