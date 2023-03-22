from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text


def register(username, password):
    # TODO: Check if user already exists
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
    try:
        sql = '''SELECT name, password FROM Users WHERE name = :username'''
        res = db.session.execute(text(sql), {'username': username})
        user = res.fetchone()
    except:
        pass
    if not user or not check_password_hash(user[0], password):
        return False
    session['uid'], session['username'] = user[0], user[1]
    return True


def session_uid():
    return session.get('uid', 0)


def session_username():
    return session.get('username', 0)
