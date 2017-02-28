# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, abort
from .models import Brand
from utils.decorators import authenticated

app = Blueprint('example', __name__, template_folder='templates')


@app.route("/")
def index_view():
    brands = Brand.find_all()
    return render_template("index.html", brands=brands)


@authenticated
@app.route("/account")
def secured():
    return abort(200)
