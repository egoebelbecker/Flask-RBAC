#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/api/inventory', methods=['GET'])
def query_records():
    name = request.args.get('name')
    print("Getting {}".format(name))
    with open('data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        for record in records:
            if record['name'] == name:
                return jsonify(record)
        return jsonify({'error': 'data not found'})


@app.route('/api/inventory', methods=['PUT'])
def create_record():
    record = json.loads(request.data)
    print("Putting {}".format(record))
    with open('data.txt', 'r') as f:
        data = f.read()
    if not data:
        records = [record]
    else:
        records = json.loads(data)
        records.append(record)
    with open('data.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(record)


@app.route('/api/inventory', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    new_records = []
    print("Modifying {}".format(record))
    with open('data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
    for r in records:
        if r['name'] == record['name']:
            r['email'] = record['email']
        new_records.append(r)
    with open('data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(record)


@app.route('/api/inventory', methods=['DELETE'])
def delete_record():
    record = json.loads(request.data)
    new_records = []
    print("Deleting {}".format(record))
    with open('data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        for r in records:
            if r['name'] == record['name']:
                continue
            new_records.append(r)
    with open('data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(record)


if __name__ == '__main__':
    app.run(port=8080)