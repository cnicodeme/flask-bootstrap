# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, request, abort
from .models import Brand, SKU
from utils.decorators import authenticated

app = Blueprint('example', __name__, template_folder='templates')


@app.route("/")
def index_view():
    return render_template("index.html")


@authenticated
@app.route("/account")
def secured():
    return abort(200)
