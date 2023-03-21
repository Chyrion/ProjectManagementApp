from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text


def register(username, password):
    exists = False
    # Check if the user already exists
    # try:
    #     sql = '''SELECT name FROM Users WHERE name = :name'''
    #     res = db.session.execute(sql, {'name': username})
    #     user = res.fetchone()
    #     if user[1] == username:
    #         exists = True
    # except:
    #     return False
    # if not exists:
    pass_hash = generate_password_hash(password)
    try:
        sql = '''INSERT INTO Users (name, password) VALUES (:username, :password)'''
        db.session.execute(
            text(sql), {'username': username, 'password': pass_hash})
        db.session.commit()
    except:
        return False
    return True


def login(username, password):
    sql = '''SELECT name, password FROM Users WHERE name = :username'''
    res = db.session.execute(text(sql), {'username': username})
    user = res.fetchone()
    if not user or not check_password_hash(user[0], password):
        return False
    session['uid'], session['username'] = user[0], user[1]
    return True


def get_session():
    return {'uid': session.get('uid', 0), 'username': session.get('username', 0)}
