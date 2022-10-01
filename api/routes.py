from flask import jsonify, request
from api import app, local_environment, db


@app.route('/', methods=['GET'])
def check_active():
    return jsonify({'active': True})

