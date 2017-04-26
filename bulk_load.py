""" MetaDB bulk processing tools.

load: import data from bulk_lookup into the database

Usage:
    bulk_load.py lastfm metadb.scrapers.recording.lastfm/

first argument is the name of the source
second argument is the directory created by bulk_lookup

"""

import argparse
import sys
import os
import time
import json

from metadb import util
from metadb import log

import metadb.db
import config
import metadb.data

def bulk_import_some_items(scraper, filenames):
    with metadb.db.engine.begin() as connection:
        for fname in filenames:
            try:
                data = json.load(open(fname))
                mbid = os.path.splitext(os.path.basename(fname))[0]
                metadb.data._add_item_w_connection(connection, scraper, mbid, data=data)
            except ValueError:
                log.warn("{}: not valid json".format(fname))


def load(sourcename, thedir):
    metadb.db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)

    source = metadb.data.load_source(sourcename)
    if not source:
        log.warn("No source with this name")
        sys.exit(1)
    scraper = metadb.data.load_latest_scraper_for_source(source)
    if not scraper:
        log.warn("No scraper for this source")
        sys.exit(1)

    if not os.path.exists(thedir) or not os.path.isdir(thedir):
        log.warn("{}: not a directory".format(thedir))
        sys.exit(1)

    allfiles = []
    for root, dirs, files in os.walk(thedir):
        for fname in files:
            allfiles.append(os.path.join(root, fname))

    total = len(allfiles)
    log.info("Got {} items to add.".format(total))

    done = 0
    starttime = time.monotonic()
    SIZE = 1000
    for fnames in util.chunks(allfiles, SIZE):
        bulk_import_some_items(scraper, fnames)

        done += SIZE
        durdelta, remdelta = util.stats(done, total, starttime)
        log.info("Done %s/%s in %s; %s remaining", done, total, str(durdelta), str(remdelta))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("source")
    a.add_argument("directory")

    args = a.parse_args()
    load(args.source, args.directory)

if __name__ == "__main__":
    main()
