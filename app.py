#!/usr/bin/env python
# encoding: utf-8
import json
import sqlite3
from flask import Flask, request, jsonify, abort


conn = sqlite3.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS inventory (name TEXT NOT NULL UNIQUE, data json NOT NULL)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_name on inventory(name)')
conn.close()

# Retrieve an item
@app.route('/api/inventory', methods=['GET'])
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
def update_record():
    try:
        record = json.loads(request.data)
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO inventory (name, data) VALUES(?, ?) ON CONFLICT(name) DO UPDATE SET data=?",(record['name'], request.data, request.data))
            con.commit()
        return jsonify(record)
    except Exception as e:
        abort(500, e)

# Add a new item
@app.route('/api/inventory', methods=['POST'])
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


if __name__ == '__main__':
    app.run()
