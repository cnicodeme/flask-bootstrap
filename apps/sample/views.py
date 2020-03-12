# -*- coding:utf-8 -*-

from flask import Blueprint, jsonify
from utils.decorators import authenticated


app = Blueprint('sample', __name__)


@app.route('/', methods=['GET'])
@authenticated
def details():
    return jsonify({
        'success': True
    })
