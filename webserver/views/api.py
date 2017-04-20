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


@api_bp.route("/lookup_meta", methods=["POST"])
@api_bp.route("/lookup_meta/<uuid:mbid>", methods=["POST"])
@webserver.decorators.admin_required
def lookup_metadata(mbid=None):
    """Force a lookup of metadata for recordings which are added but not in
       the musicbrainz metadata tables."""

    if mbid:
        metadb.jobs.scrape_musicbrainz.delay(m)
    else:
        missing = metadb.data.get_recordings_missing_meta()
        for m in missing:
            metadb.jobs.scrape_musicbrainz.delay(m)

    return jsonify({})


@api_bp.route("/scrape/<source_name>", methods=["POST"])
@api_bp.route("/scrape/<source_name>/<uuid:mbid>", methods=["POST"])
@webserver.decorators.admin_required
def scrape(source_name, mbid=None):
    source = metadb.data.load_source(source_name)
    scraper = metadb.data.load_latest_scraper_for_source(source)

    if scraper["mb_type"] == "recording":
        metadata = metadb.data.get_unprocessed_recordings_for_scraper(scraper, mbid)
    elif scraper["mb_type"] == "release_group":
        metadata = metadb.data.get_unprocessed_release_groups_for_scraper(scraper, mbid)

    for m in metadata:
        metadb.jobs.scrape.delay(scraper, m)

    return jsonify({})


@api_bp.route("/<uuid:mbid>/<source_name>")
def load(mbid, source_name):
    data = metadb.data.load_item(mbid, source_name)
    if not data:
        raise webserver.exceptions.APINotFound("Not found")
    return jsonify(data)

