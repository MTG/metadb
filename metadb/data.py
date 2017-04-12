import json
import uuid
import pytz
import dateparser

from sqlalchemy.sql import text

from . import db


def add_token(admin=False):
    """ Add a new token to the database and return it
        Arguments:
          admin: True if this token has admin privileges
    """
    query = text("""
        INSERT INTO token (token, admin)
             VALUES (:token, :admin)""")
    with db.engine.begin() as connection:
        token = str(uuid.uuid4())
        result = connection.execute(query, {"token": token, "admin": admin})
        return token


def remove_token(token):
    try:
        uuid.UUID(token, version=4)
    except ValueError:
        return
    query = text("""
        DELETE FROM token
              WHERE token = :token""")
    with db.engine.begin() as connection:
        connection.execute(query, {"token": token})


def get_tokens():
    query = text("""
        SELECT token::text
             , admin
          FROM token
      ORDER BY added""")
    with db.engine.begin() as connection:
        rows = connection.execute(query)
        return [dict(r) for r in rows.fetchall()]


def get_token(token):
    try:
        uuid.UUID(token, version=4)
    except ValueError:
        return {}
    query = text("""
        SELECT token::text
             , admin
          FROM token
         WHERE token = :token""")
    with db.engine.begin() as connection:
        result = connection.execute(query, {"token": token})
        if result.rowcount:
            return dict(result.fetchone())
        else:
            return {}


def add_source(name):
    query = text("""
        INSERT INTO source (name)
             VALUES (:name)
          RETURNING id""")
    with db.engine.begin() as connection:
        result = connection.execute(query, {"name": name})
        id = result.fetchone()[0]
        return {"name": name, "id": id}


def add_recording_mbids(mbids):
    """ Add some recording musicbrainzids to the recording table.
        Returns mbids which were added.
    """
    check_query = text("""
        SELECT mbid
          FROM recording
         WHERE mbid = :mbid""")
    insert_query = text("""
        INSERT INTO recording (mbid)
             VALUES (:mbid)""")
    ret = []
    with db.engine.begin() as connection:
        for mbid in mbids:
            result = connection.execute(check_query, {"mbid": mbid})
            if not result.rowcount:
                connection.execute(insert_query, {"mbid": mbid})
                ret.append(mbid)
    return ret


def get_recording_mbids():
    query = text("""
        SELECT mbid::text
          FROM recording
      ORDER BY added""")
    with db.engine.begin() as connection:
        result = connection.execute(query)
        return [dict(r) for r in result.fetchall()]


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


def add_scraper(source, module, version, description):
    query = text("""
        INSERT INTO scraper (source_id, module, version, description)
             VALUES (:source_id, :module, :version, :description)
          RETURNING id
        """)
    with db.engine.begin() as connection:
        result = connection.execute(query, {"source_id": source["id"],
                                            "module": module,
                                            "version": version,
                                            "description": description})
        row = result.fetchone()
        return {"id": row.id, "module": module,
                "version": version, "description": description}


def load_scrapers_for_source(source):
    query = text("""
        SELECT id
             , source_id
             , module
             , version
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
                        "module": r.module})
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


def add_item(scraper, mbid, data):
    with db.engine.begin() as connection:
        return _add_item_w_connection(connection, scraper, mbid, data)


def _add_item_w_connection(connection, scraper, mbid, data):
    item_query = text("""
        INSERT INTO item (scraper_id, mbid)
             VALUES (:scraper_id, :mbid)
          RETURNING id
        """)

    item_data_query = text("""
        INSERT INTO item_data (item_id, data)
             VALUES (:item_id, :data)
        """)

    result = connection.execute(item_query, {"scraper_id": scraper["id"],
                                             "mbid": mbid})
    row = result.fetchone()
    id = row.id
    if isinstance(data, dict):
        data = json.dumps(data)
    connection.execute(item_data_query, {"item_id": id,
                                         "data": data})

    return {"id": id, "mbid": mbid, "scraper_id": scraper["id"],
            "data": data}


def get_recordings_missing_meta():
    query = text("""
        SELECT recording.mbid::text
          FROM recording
     LEFT JOIN recording_meta
         USING (mbid)
         WHERE recording_meta.mbid IS NULL""")
    with db.engine.begin() as connection:
        result = connection.execute(query)
        return [r[0] for r in result.fetchall()]


def load_item(mbid, source_name):
    source = load_source(source_name)
    scraper = load_latest_scraper_for_source(source)
    query = text("""
        SELECT item.id,
               item.mbid,
               item.added,
               item_data.data
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
                    "data": row.data}

    return None


def _get_recording_meta(connection, recording_mbid):
    # We want to return the timezone always in UTC, regardless of how it's stored in
    # the database, but if you specify a timezone, pg won't return it in the data,
    # so we add utc back on before returning it.
    query = text("""
      SELECT mbid::text
           , name
           , artist_credit
           , last_updated AT TIME ZONE 'UTC' AS last_updated
        FROM recording_meta
      WHERE mbid = :mbid""")
    result = connection.execute(query, {"mbid": recording_mbid})
    row = result.fetchone()
    if row:
        row = dict(row)
        lu = row.get("last_updated")
        if lu:
            row["last_updated"] = lu.replace(tzinfo=pytz.utc)
    return row


def get_recording_meta(recording_mbid):
    with db.engine.begin() as connection:
        return _get_recording_meta(connection, recording_mbid)


def cache_musicbrainz_metadata(recording):
    """
    Convert metadata from the musicbrainz scraper into the metadata tables

    recording_meta
    recording_release_group
    release_group
    release_group_meta
    :param recording:
    :return:
    """

    with db.engine.begin() as connection:
        _add_recording_meta(connection, recording)
        for rg in recording["release_group_map"].values():
            _add_release_group_meta(connection, rg)
            _add_link_recording_release_group(connection, recording["mbid"], rg["mbid"])


def _add_recording_meta(connection, recording):
    """

    :param connection:
    :param recording: A dictionary of metadata with keys mbid, name, artist_credit, last_updated
                      last_updated must be a datetime object.
    :return:
    """

    existing = _get_recording_meta(connection, recording["mbid"])
    if existing:
        # If this recording exists, and has a last updated date equal to the one we
        # are trying to add, skip it
        existing_date = existing["last_updated"]
        current_date = recording["last_updated"]
        if existing_date >= current_date:
            return

        query = text("""
          UPDATE recording_meta
             SET name = :name
               , artist_credit = :ac
               , last_updated = :last_updated
           WHERE mbid = :mbid""")
        # Otherwise we perform an update
    else:
        # If the there is no existing recording, do an insert
        query = text("""
          INSERT INTO recording_meta (mbid, name, artist_credit, last_updated)
                              VALUES (:mbid, :name, :ac, :last_updated)""")

    connection.execute(query, {"mbid": recording["mbid"],
                               "name": recording["name"],
                               "ac": recording["artist_credit"],
                               "last_updated": recording["last_updated"]})


def get_release_group_meta(release_group_mbid):
    with db.engine.connect() as connection:
        return _get_release_group_meta(connection, release_group_mbid)


def _get_release_group_meta(connection, release_group_mbid):
    query = text("""
        SELECT mbid::text
             , name
             , artist_credit
             , first_release_date
             , last_updated AT TIME ZONE 'UTC' AS last_updated
          FROM release_group_meta
         WHERE mbid = :mbid""")
    result = connection.execute(query, {"mbid": release_group_mbid})
    row = result.fetchone()
    if row:
        row = dict(row)
        lu = row.get("last_updated")
        if lu:
            row["last_updated"] = lu.replace(tzinfo=pytz.utc)
    return row


def get_release_groups_for_recording(recording_mbid):
    query = text("""
        SELECT release_group_mbid::text
          FROM recording_release_group
         WHERE recording_mbid = :recording_mbid""")
    with db.engine.connect() as connection:
        result = connection.execute(query, {"recording_mbid": recording_mbid})
        ret = []
        for row in result.fetchall():
            ret.append(row[0])
        return ret


def _add_release_group_meta(connection, release_group):

    # See if the release group exists, and add it if not:
    existing_rg = _get_release_group_meta(connection, release_group["mbid"])
    if existing_rg:
        existing_last_updated = existing_rg["last_updated"]
        current_last_updated = release_group["last_updated"]
        # If `last_updated` hasn't changed, return
        if existing_last_updated >= current_last_updated:
            return

        # Otherwise update the existing meta
        query_rg_meta = text("""
                UPDATE release_group_meta
                   SET name = :name
                     , artist_credit = :artist_credit
                     , first_release_date = :first_release_date
                     , last_updated = :last_updated
                 WHERE mbid = :rg_mbid""")
    else:  # insert
        query_rg_meta = text("""
              INSERT INTO release_group_meta (mbid, name, artist_credit, first_release_date, last_updated)
                   VALUES (:rg_mbid, :name, :artist_credit, :first_release_date, :last_updated)""")

        query_insert_rg = text("""INSERT INTO release_group (mbid) VALUES (:mbid)""")
        connection.execute(query_insert_rg, {"mbid": release_group["mbid"]})

    # This will be an update or an insert
    connection.execute(query_rg_meta, {"rg_mbid": release_group["mbid"],
                                       "name": release_group["name"],
                                       "artist_credit": release_group["artist_credit"],
                                       "first_release_date": release_group["first_release_date"],
                                       "last_updated": release_group["last_updated"]})


def _add_link_recording_release_group(connection, recording_mbid, release_group_mbid):
    # See if there is a link between the RG and this recording_id
    query_check_recording_rg = text("""
      SELECT *
        FROM recording_release_group
       WHERE recording_mbid = :recording_mbid
         AND release_group_mbid = :release_group_mbid""")
    result_has_recording_rg = connection.execute(query_check_recording_rg,
                                                 {"recording_mbid": recording_mbid,
                                                  "release_group_mbid": release_group_mbid})
    if not result_has_recording_rg.rowcount:
        query_insert_recording_rg = text("""
          INSERT INTO recording_release_group (recording_mbid, release_group_mbid)
                                       VALUES (:recording_mbid, :release_group_mbid)""")
        connection.execute(query_insert_recording_rg, {"recording_mbid": recording_mbid,
                                                       "release_group_mbid": release_group_mbid})

