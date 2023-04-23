from db import db
from flask import session, request, abort
from secrets import token_hex
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text


def register(username, password):
    # Check if user already exists
    try:
        sql_user = '''SELECT name FROM Users WHERE name = :name'''
        res = db.session.execute(text(sql_user), {'name': username})
        existing_user = res.fetchone()
    except:
        pass
    if existing_user:
        return False

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
        sql = '''SELECT id, name, password FROM Users WHERE name = :username'''
        res = db.session.execute(text(sql), {'username': username})
        user = res.fetchone()
    except:
        pass
    if not user or not check_password_hash(user[2], password):
        return False
    session['uid'], session['username'] = user[0], user[1]
    session['csrf_token'] = token_hex(16)
    return True


def logout():
    del session['uid']
    del session['username']
    return True


def check_csrf():
    if session['csrf_token'] != request.form['csrf_token']:
        abort(403)


def session_uid() -> int:
    return session.get('uid', 0)


def session_username():
    return session.get('username', 0)
