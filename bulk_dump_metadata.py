import argparse
import sys
import csv
import collections

from sqlalchemy import text

import metadb.db
import metadb.data
import metadb.scrapers
import config

metadb.db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)



def dump(sourcename, extradata=None, include_recordings=False):
    source = metadb.data.load_source(sourcename)
    scraper = metadb.data.load_latest_scraper_for_source(source)
    if scraper["mb_type"] == "release_group" and include_recordings:
        # Provide mappings at a recording level
        pass
    s_obj = metadb.scrapers.create_scraper_object(scraper)
    if not hasattr(s_obj, "parse_db_data"):
        raise Exception("Module for parser {} doesn't have a .parse_db_data method".format(sourcename))

    if extradata and not hasattr(s_obj, "config_dump"):
        raise Exception("You specified extra data, but module for parser {} doesn't have a .config_dump method to load it".format(sourcename))

    if extradata:
        s_obj.config_dump(extradata)

    query = text("""
      SELECT mbid::text
           , data
        FROM item
        JOIN item_data
          ON item_id = item.id
       WHERE scraper_id = :id""")

    recording_rg_query = text("""
      SELECT recording_mbid::text
           , release_group_mbid::text
        FROM recording_release_group""")

    with metadb.db.engine.begin() as connection:
        w = csv.writer(sys.stdout, delimiter="\t")
        release_group_recordings = collections.defaultdict(list)
        if include_recordings:
            res = connection.execute(recording_rg_query)
            for rec, rg in res.fetchall():
                release_group_recordings[rg].append(rec)

        res = connection.execute(query, {"id": scraper["id"]})
        for row in res.fetchall():
            mbid, data = row
            if include_recordings:
                recording_mbids = release_group_recordings.get(mbid, [])
                # TODO: Now this param could be a list or a value. Adding another parameter makes recording scrapers weird
                # todo: what about having 2 methods? one for recording data and one for releases?
                mbid = recording_mbids
            s_obj.parse_db_data(mbid, data, w)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--recording", action="store_true", help="If the source is a release, dump data for all recordings in each release", required=False)
    parser.add_argument("--data", help="Additional data file if required by scraper (e.g. genre tree)", required=False)
    parser.add_argument("source")
    args = parser.parse_args()
    dump(args.source, args.data, args.recording)
