from metadb import db
from metadb import data
import config
from metadb import log
from metadb import util

from sqlalchemy import text
import time

def main():
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)
    source = data.load_source("musicbrainz")
    scraper = data.load_latest_scraper_for_source(source)

    recordings = get_recordings()
    total = len(recordings)
    done = 0
    starttime = time.time()
    log.info("starting..., %s recordings to process", total)

    for reclist in util.chunks(recordings, 10000):
        log.info("have %s recordings", len(reclist))
        with db.engine.connect() as connection:
            saveddata = get_data(connection, scraper["id"], reclist)
            log.info(" - got %s rows matching them", len(saveddata))
            process(connection, saveddata)
        done += len(reclist)
        durdelta, remdelta = util.stats(done, total, starttime)
        log.info("Done %s/%s in %s; %s remaining", done, total, str(durdelta), str(remdelta))

def get_data(connection, scraperid, recordings):
    query = text("""
        SELECT item.mbid
             , item_data.data
          FROM item
     LEFT JOIN item_data
            ON item_data.item_id = item.id
           AND item.scraper_id = :scraper_id
         WHERE item.mbid in :mbids
    """)
    res = connection.execute(query, {"scraper_id": scraperid,
        "mbids": tuple(recordings)})
    return [(r[0], r[1]) for r in res]


def process(connection, datalist):
    added = 0
    for recmbid, item in datalist:
        data = item["result"]
        if not data:
            continue
        recording_title = data["name"]
        rec_artist_credit = data["artist_credit"]
        add_to_recmeta(connection, recmbid, recording_title, rec_artist_credit)
        added += 1

        for rgmbid, rgdata in data["release_group_map"].items():
            rgtitle = rgdata["name"]
            earliest_date = rgdata["first_release_date"]
            rgartist_credit = rgdata["artist_credit"]
            add_to_rg(connection, rgmbid, recmbid, rgtitle, rgartist_credit, earliest_date)

    log.info(" * added %s recordings", added)

def get_recordings():
    existingq = text("SELECT distinct(recording_mbid) FROM release_group")
    allq = text("SELECT mbid FROM recording")
    with db.engine.connect() as connection:
        res = connection.execute(existingq)
        existing = set([r[0] for r in res])
        res = connection.execute(allq)
        recids = [r[0] for r in res]
        recids = [r for r in recids if r not in existing]
        return recids


def add_to_recmeta(connection, mbid, title, artist):
    query = text("""
        INSERT INTO recording_meta
                    (mbid, title, artist_credit)
             VALUES (:mbid, :title, :artist_credit)""")
    connection.execute(query, {"mbid": mbid, "title": title,
                               "artist_credit": artist})


def add_to_rg(connection, mbid, recmbid, title, artist, date):
    query = text("""
        INSERT INTO release_group
                    (mbid, recording_mbid, title, artist_credit, earliest_date)
             VALUES (:mbid, :recording_mbid, :title, :artist_credit, :earliest_date)""")
    connection.execute(query, {"mbid": mbid, "recording_mbid": recmbid, "title": title,
                               "artist_credit": artist, "earliest_date": date})

if __name__ == "__main__":
    main()

