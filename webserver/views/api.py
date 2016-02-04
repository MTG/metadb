from __future__ import absolute_import
from flask import Blueprint, jsonify

import metadb
import metadb.data

import webserver.exceptions

api_bp = Blueprint('api', __name__)

@api_bp.route("/<uuid:mbid>/<source_name>")
def load(mbid, source_name):
    data = metadb.data.load_item(mbid, source_name)
    if not data:
        raise webserver.exceptions.APINotFound("Not found")
    return jsonify(data)

