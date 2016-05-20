from metadb.scrapers.recording import musicbrainzdb
from metadb import db, data
import config
from metadb import log
from metadb import util

import time
import concurrent.futures

from sqlalchemy import text

def get_mbids():
    source = data.load_source("musicbrainz")
    scraper = data.load_latest_scraper_for_source(source)

    existing = text("""
        SELECT mbid::text
          FROM item
         WHERE scraper_id = :scraper_id""")


    q = "SELECT mbid::text FROM recording"
    with db.engine.connect() as connection:
        res = connection.execute(existing, {"scraper_id": scraper["id"]})
        existing = [r[0] for r in res]
        log.info("got %s existing items", len(existing))
        existing = set(existing)
        res = connection.execute(q)
        remaining = [r[0] for r in res if r[0] not in existing]
        log.info("remaining %s", len(remaining))
        return remaining

def query(mbid):
    session = musicbrainzdb.Session()

    result, result_type = musicbrainzdb.scrape({"mbid": mbid, "session": session})
    result = {
                'type': result_type,
                'mbid': mbid,
                'scraper': "metadb.scrapers.recording.musicbrainzdb",
                'result': result
             }
    session.close()
    return result

def lookup(mbids, scraper):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_mbid = {}
        for m in mbids:
            future_to_mbid[executor.submit(query, m)] = m
        for future in concurrent.futures.as_completed(future_to_mbid):
            m = future_to_mbid[future]
            try:
                result = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (m, exc))
            else:
                data.add_item(scraper, m, data=result)

def main():
    db.init_db_engine(config.SQLALCHEMY_DATABASE_URI)
    source = data.load_source("musicbrainz")
    scraper = data.load_latest_scraper_for_source(source)
    print(scraper)

    mbids = get_mbids()
    total = len(mbids)

    starttime = time.time()
    done = 0
    for mblist in util.chunks(mbids, 100):
        lookup(mblist, scraper)
        done += 100
        durdelta, remdelta = util.stats(done, total, starttime)
        log.info("Done %s/%s in %s; %s remaining", done, total, str(durdelta), str(remdelta))


if __name__ == "__main__":
    main()
