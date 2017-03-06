import uuid

from flask import request, Blueprint, jsonify

import metadb
import metadb.data
import webserver.exceptions
import webserver.decorators

import metadb.jobs

api_bp = Blueprint('api', __name__)

@api_bp.route("/recordings", methods=["POST"])
@webserver.decorators.admin_required
def submit_recordings():
    data = request.get_json()
    if not isinstance(data, list):
        raise webserver.exceptions.APIBadRequest("Submitted data must be a list")
    newdata = []
    for d in data:
        try:
            uuid.UUID(str(d), version=4)
            newdata.append(d)
        except ValueError:
            pass

    added = metadb.data.add_recording_mbids(newdata)
    for a in added:
        metadb.jobs.scrape_musicbrainz.delay(a)
    return jsonify({})


@api_bp.route("/<uuid:mbid>/<source_name>")
def load(mbid, source_name):
    data = metadb.data.load_item(mbid, source_name)
    if not data:
        raise webserver.exceptions.APINotFound("Not found")
    return jsonify(data)

