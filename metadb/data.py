import logging
import json
from . import exceptions
import uuid
from sqlalchemy.sql import text

from . import db

from . import exceptions

def add_source(name):
    query = text("""
        INSERT INTO source (name)
             VALUES (:name)
          RETURNING id""")
    with db.engine.begin() as connection:
        result = connection.execute(query, {"name": name})
        id = result.fetchone()[0]
        return {"name": name, "id": id}

def load_source(name):
    query = text("""
        SELECT id
             , name
          FROM source
         WHERE name = :name""")
    with db.engine.begin() as connection:
        result = connection.execute(query, {"name": name})
        row = result.fetchone()
        if row:
            return {"id": row.id, "name": row.name}
    return None

def add_scraper(source, version, scraper):
    query = text("""
        INSERT INTO scraper (source_id, version, scraper)
             VALUES (:source_id, :version, :scraper)
          RETURNING id
        """)
    with db.engine.begin() as connection:
        result = connection.execute(query, {"source_id": source["id"],
                                            "version": version,
                                            "scraper": scraper})
        row = result.fetchone()
        return {"id": row.id, "version": version, "scraper": scraper}

def load_scrapers_for_source(source):
    query = text("""
        SELECT id
             , source_id
             , version
             , scraper
          FROM scraper
         WHERE source_id = :source_id
        """)
    with db.engine.begin() as connection:
        result = connection.execute(query, {"source_id": source["id"]})
        rows = result.fetchall()
        ret = []
        for r in rows:
            ret.append({"id": r.id,
                    "source_id": r.source_id,
                    "version": r.version,
                    "scraper": r.scraper})
        return ret

def load_latest_scraper_for_source(source):
    query = text("""
        SELECT id
             , source_id
             , version
             , scraper
          FROM scraper
         WHERE source_id = :source_id
      ORDER BY version DESC
         LIMIT 1
        """)
    with db.engine.begin() as connection:
        result = connection.execute(query, {"source_id": source["id"]})
        row = result.fetchone()
        if row:
            return {"id": row.id,
                    "source_id": row.source_id,
                    "version": row.version,
                    "scraper": row.scraper}
    return None

def add_item(scraper, mbid, request=None, response=None, data=None):
    if response is None and data is None:
        raise exceptions.BadDataException("Need either a response or data")

    item_query = text("""
        INSERT INTO item (scraper_id, mbid)
             VALUES (:scraper_id, :mbid)
          RETURNING id
        """)

    item_data_query = text("""
        INSERT INTO item_data (item_id, data, request, response)
             VALUES (:item_id, :data, :request, :response)
        """)
    with db.engine.begin() as connection:
        result = connection.execute(item_query, {"scraper_id": scraper["id"],
                                                 "mbid": mbid})
        row = result.fetchone()
        id = row.id
        result = connection.execute(item_data_query, {"item_id": id,
                                                      "data": json.dumps(data),
                                                      "request": request,
                                                      "response": response})
        return {"id": id, "mbid": mbid, "scraper_id": scraper["id"],
                "data": data, "request": request, "response": response}

def load_item(mbid, source_name):
    source = load_source(source_name)
    scraper = load_latest_scraper_for_source(source)
    query = text("""
        SELECT item.id,
               item.mbid,
               item.added,
               item_data.data,
               item_data.request,
               item_data.response
          FROM item
     LEFT JOIN item_data
            ON item_data.item_id = item.id
         WHERE item.mbid = :mbid
           AND item.scraper_id = :scraper_id
        """)
    with db.engine.begin() as connection:
        result = connection.execute(query, {"scraper_id": scraper["id"],
                                            "mbid": mbid})
        row = result.fetchone()
        if row:
            return {"id": row.id, "mbid": row.mbid, "added": row.added,
                    "data": row.data, "request": row.request, "response": row.response}

    return None


