import config

import operator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mbdata import models

engine = create_engine(config.MUSICBRAINZ_DATABASE_URI) #, echo=True)
Session = sessionmaker(bind=engine)

TYPE = "recording"
s = None


def sort_tags(tags):
    # Tags from webservice are strings, let's make them all integer
    tags = [{"name": t["name"], "count": int(t["count"])} for t in tags]
    return sorted(tags, key=operator.itemgetter("name"))


def config():
    global s
    s = Session()


def load_recording(session, recordingid):
    rec = session.query(models.Recording).filter_by(gid=recordingid).first()
    if rec is None:
        redir = session.query(models.RecordingGIDRedirect).filter_by(gid=recordingid).first()
        if redir is None:
            return None
        return redir.recording
    return rec


def recording_to_releases(session, recording):
    tracks = session.query(models.Track).filter_by(recording=recording)
    releases = set()
    for t in tracks:
        medium = t.medium
        release = medium.release
        releases.add(release)
    return list(releases)


def recording_tags(session, recording):
    tags = session.query(models.RecordingTag).filter_by(recording=recording)
    return [{"name": t.tag.name, "count": t.count} for t in tags]


def release_tags(session, release):
    tags = session.query(models.ReleaseTag).filter_by(release=release)
    return [{"name": t.tag.name, "count": t.count} for t in tags]


def release_group_tags(session, release_group):
    tags = session.query(models.ReleaseGroupTag).filter_by(release_group=release_group)
    return [{"name": t.tag.name, "count": t.count} for t in tags]


def artist_tags(session, artist):
    tags = session.query(models.ArtistTag).filter_by(artist=artist)
    return [{"name": t.tag.name, "count": t.count} for t in tags]


def join_artist_credit(artist_credit):
    credit = artist_credit.name
    artists = [a.artist.gid for a in artist_credit.artists]
    return credit, artists


def format_date(part_date):
    if not part_date.year:
        return None

    parts = [str(part_date.year)]
    if part_date.month:
        parts.append("%02d" % part_date.month)
    if part_date.day:
        parts.append("%02d" % part_date.day)

    return "-".join(parts)


def format_releases(session, releases, rec_artists):
    release_groups = set()

    all_releases = {}
    for r in releases:
        ac, artists = join_artist_credit(r.artist_credit)
        tags = release_tags(session, r)
        release_groups.add(r.release_group)
        release_dates = []
        for d in r.country_dates:
            formatted = format_date(d.date)
            if formatted:
                release_dates.append(formatted)
        for d in r.unknown_country_dates:
            formatted = format_date(d.date)
            if formatted:
                release_dates.append(formatted)

        for acn in r.artist_credit.artists:
            rec_artists.add(acn.artist)

        all_releases[r.gid] = {
            "name": r.name,
            "id": r.gid,
            "release_group": r.release_group.gid,
            "release_dates": sorted(release_dates),
            "artist_credit": ac,
            "artists": sorted(artists),
            "tags": sort_tags(tags),
            }

    return all_releases, rec_artists, release_groups


def format_release_groups(session, rgs, rec_artists):
    all_release_groups = {}

    for rg in rgs:
        tags = release_group_tags(session, rg)
        ac, artists = join_artist_credit(rg.artist_credit)

        for acn in rg.artist_credit.artists:
            rec_artists.add(acn.artist)

        first_release_date = format_date(rg.meta.first_release_date)
        if not first_release_date:
            first_release_date = ""

        all_release_groups[rg.gid] = {
                "name": rg.name,
                "first_release_date": first_release_date,
                "artist_credit": ac,
                "artists": sorted(artists),
                "tags": sort_tags(tags)}

    return all_release_groups, rec_artists


def format_artists(session, artists):
    all_artists = {}

    for a in artists:
        tags = artist_tags(session, a)
        all_artists[a.gid] = {"name": a.name,
                              "tags": sort_tags(tags)}
    return all_artists


def scrape(query):
    mbid = query['mbid']
    session = s

    rec = load_recording(session, mbid)
    rec_artists = set()
    data = {}
    if rec:
        tags = recording_tags(session, rec)

        releases = recording_to_releases(session, rec)
        ac, artists = join_artist_credit(rec.artist_credit)
        for acn in rec.artist_credit.artists:
            rec_artists.add(acn.artist)

        track_releases = []
        for r in releases:
            track_releases.append(r.gid)

        all_releases, rec_artists, release_groups = format_releases(session, releases, rec_artists)
        all_release_groups, rec_artists = format_release_groups(session, release_groups, rec_artists)
        all_artists = format_artists(session, list(rec_artists))

        data["name"] = rec.name
        data["artist_credit"] = ac
        data["artists"] = sorted(artists)
        data["tags"] = sort_tags(tags)
        data["releases"] = sorted(track_releases)

        data["artist_map"] = all_artists
        data["release_map"] = all_releases
        data["release_group_map"] = all_release_groups

    return data
