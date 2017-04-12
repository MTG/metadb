import os

from . import musicbrainzdb
from . import musicbrainzws


def config():
    db = os.getenv("METADB_MUSICBRAINZ_DB_URI")
    # If database config exists, use db. else ws
    if db:
        musicbrainzdb.config()
    else:
        musicbrainzws.config()


def dispose():
    db = os.getenv("METADB_MUSICBRAINZ_DB_URI")
    # If database config exists, use db. else ws
    if db:
        musicbrainzdb.dispose()
    else:
        musicbrainzws.dispose()


def scrape(query):
    db = os.getenv("METADB_MUSICBRAINZ_DB_URI")
    # If database config exists, use db. else ws
    if db:
        return musicbrainzdb.scrape(query)
    else:
        return musicbrainzws.scrape(query)
