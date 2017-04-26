import argparse
import sys
import csv

from sqlalchemy import text

import metadb.db
import metadb.data
import metadb.scrapers
import config

metadb.db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)



def dump(sourcename):
    source = metadb.data.load_source(sourcename)
    scraper = metadb.data.load_latest_scraper_for_source(source)
    s_obj = metadb.scrapers.create_scraper_object(scraper)
    if not hasattr(s_obj, "parse_db_data"):
        raise Exception("Module for parser {} doesn't have a .parse_db_data method".format(sourcename))

    query = text("""
      SELECT mbid::text
           , data
        FROM item
        JOIN item_data
          ON item_id = item.id
       WHERE scraper_id = :id""")

    with metadb.db.engine.begin() as connection:
        w = csv.writer(sys.stdout)
        res = connection.execute(query, {"id": scraper["id"]})
        for row in res.fetchall():
            mbid, data = row
            s_obj.parse_db_data(mbid, data, w)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    args = parser.parse_args()
    dump(args.source)


if __name__ == "__main__":
    main()
