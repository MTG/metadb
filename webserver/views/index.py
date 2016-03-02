from __future__ import absolute_import
from flask import Blueprint, render_template

import metadb
import metadb.data

import webserver.exceptions

index_bp = Blueprint('index', __name__)

@index_bp.route("/")
def index():
    return render_template("index.html")


