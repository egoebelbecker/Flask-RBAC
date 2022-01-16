#!/usr/bin/env python
# encoding: utf-8
import json
import sqlite3
from flask import Flask, request, jsonify, abort,
from werkzeug.security import check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required
import base64
from functools import wraps
from enum import IntEnum


app = Flask(__name__)
app.secret_key = "ITJUSTDOESNTMATTER"

login_manager = LoginManager()
login_manager.init_app(app)


class Role(IntEnum):
    MANAGER = 3
    WAREHOUSE = 2
    SALES = 1


class User:
    def __init__(self, name, role):
        self.name = name
        self.access_level = Role.SALES
        if role == 'manager':
            self.access_level = Role.MANAGER
        elif role == 'warehouse':
            self.access_level = Role.WAREHOUSE

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.name

    def get_role(self):
        return self.access_level

    def allowed(self, access_level):
        return self.access_level >= access_level


def check_access(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)

            if not current_user.allowed(access_level):
                return abort(401)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Retrieve an item
@app.route('/api/inventory', methods=['GET'])
@login_required
@check_access(Role.SALES)
def query_records():
    try:
        name = request.args.get('name')
        with sqlite3.connect("database.db") as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("select data from inventory where name=?", (name, ))
            row = cur.fetchone()
            return row["data"] if row else ("{} not found".format(name), 400)
    except Exception as e:
        abort(500, e)


# Modify an existing item
@app.route('/api/inventory', methods=['PUT'])
@check_access(Role.WAREHOUSE)
def update_record():
    try:
        record = json.loads(request.data)
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO inventory (name, data) VALUES(?, ?) ON CONFLICT(name) DO UPDATE SET data=?", (record['name'], request.data, request.data))
            con.commit()
        return jsonify(record)
    except Exception as e:
        abort(500, e)


# Add a new item
@app.route('/api/inventory', methods=['POST'])
@check_access(Role.MANAGER)
def create_record():
    try:
        record = json.loads(request.data)
        print("Putting {}".format(record))
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO inventory (name, data) VALUES(?, ?)", (record['name'], request.data))
            con.commit()
        return jsonify(record)
    except Exception as e:
        abort(500, e)


# Delete an item
@app.route('/api/inventory', methods=['DELETE'])
@check_access(Role.MANAGER)
def delete_record():
    try:
        name = request.args.get('name')
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM inventory where name = ?", (name, ))
            con.commit()

        return "{} deleted".format(name), 200
    except Exception as e:
        abort(500, e)


@login_manager.request_loader
def load_user_from_request(request_info):

    # Try to login using Basic Auth
    auth_header = request_info.headers.get('Authorization')
    if auth_header:
        auth_header = auth_header.replace('Basic ', '', 1)
        try:
            login_info = base64.b64decode(auth_header)
            login_text = login_info.decode()
            login_info = login_text.split(':')

            user_info = retrieve_user(login_info[0])

            if check_password_hash(user_info['password'], login_info[1]):
                user = User(user_info['name'], user_info['role'])
                login_user(user)
                return user

        except TypeError as e:
            print(e)
            return None


def retrieve_user(username):
    with sqlite3.connect("database.db") as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from users where name=?", (username,))
        row = cur.fetchone()
        return row


if __name__ == '__main__':
    app.run()
