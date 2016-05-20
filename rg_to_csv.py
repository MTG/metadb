from metadb import db
from metadb import log
from metadb import util
import config

import csv
from sqlalchemy import text

def get_rgs():
    query = text("""
        SELECT mbid
             , title
             , artist_credit
             , earliest_date
          FROM release_group
      GROUP BY mbid, title, artist_credit, earliest_date
        """)
    with db.engine.connect() as connection:
        res = connection.execute(query)
        ret = []
        for r in res:
            ret.append({"mbid": r[0],
                        "release_title": r[1],
                        "artist": r[2],
                        "year": r[3][:4]})
        return ret

def get_recordings():
    query = text("""
        SELECT mbid
             , title
             , artist_credit
          FROM recording_meta
        """)
    with db.engine.connect() as connection:
        res = connection.execute(query)
        ret = []
        for r in res:
            ret.append({"mbid": r[0],
                        "recording": r[1],
                        "artist": r[2]})
        return ret


def main():
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    log.info("Release groups")
    releasegroups = get_rgs()
    fieldnames = ["mbid", "release_title", "artist", "year"]
    with open("release-group-meta.csv", "w") as fp:
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        for rg in releasegroups:
            w.writerow(rg)

    log.info("Recordings")
    recordings = get_recordings()
    fieldnames = ["mbid", "recording", "artist"]
    count = (len(recordings)//8) + 1
    for i, reclist in enumerate(util.chunks(recordings, count), 1):
        with open("recording-meta-{}.csv".format(i), "w") as fp:
            w = csv.DictWriter(fp, fieldnames=fieldnames)
            w.writeheader()
            for rec in reclist:
                w.writerow(rec)

if __name__ == "__main__":
    main()
