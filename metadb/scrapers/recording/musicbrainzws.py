import musicbrainzngs as mb

import operator
import datetime

import os
import logging
logging.basicConfig(level=logging.DEBUG)

TYPE = "recording"

MB_HOST_MBDOTORG = "musicbrainz.org"


def sort_tags(tags):
    # Tags from webservice are strings, let's make them all integer
    tags = [{"name": t["name"], "count": int(t["count"])} for t in tags]
    return sorted(tags, key=operator.itemgetter("name"))


def config():
    mb_host = os.getenv("MUSICBRAINZ_HOST", None)
    if not mb_host:
        mb_host = MB_HOST_MBDOTORG
    mb.set_useragent(
        "python-metadb-musicbrainz-scrape",
        "0.1",
        "https://github.com/MTG/metadb")
    mb.set_hostname(mb_host)
    if mb_host != MB_HOST_MBDOTORG:
        mb.set_rate_limit(False)


def get_releases_for_recording(recording_id):
    # Because there may be more than 25 releases for a recording, we should use
    # the browse methods

    # the browse release API endpoint doesn't let you retrieve tags for linked releases.
    # Because of this, we only gather IDs here, and return them.
    # we get artist, releasegroup, and tag information in `get_metadata_for_releases`

    offset = 0
    all_releases = []

    releases = mb.browse_releases(recording=recording_id, offset=0)
    total_releases = releases["release-count"]
    all_releases += releases["release-list"]
    offset += len(releases["release-list"])
    while len(all_releases) < total_releases:
        releases = mb.browse_releases(recording=recording_id, offset=offset)
        all_releases += releases["release-list"]
        offset += len(releases["release-list"])

    release_ids = []

    for r in all_releases:
        release_ids.append(r["id"])

    return release_ids


def get_metadata_for_releases(releases, now):
    artists = set()
    release_map = {}
    release_group_map = {}

    for r in releases:
        mbrel = mb.get_release_by_id(r, includes=["release-groups", "tags", "artist-credits"])["release"]
        rg = mbrel["release-group"]

        if r not in release_map:
            release_dates = [re["date"] for re in mbrel.get("release-event-list", []) if "date" in re]
            release_artists, _ = artist_credits_to_artist_list(mbrel["artist-credit"])
            artists.update(release_artists)
            release_map[r] = {"artist_credit": mbrel["artist-credit-phrase"],
                              "artists": sorted(release_artists),
                              "id": mbrel["id"],
                              "last_updated": now,
                              "name": mbrel["title"],
                              "release_dates": sorted(release_dates),
                              "release_group": rg["id"],
                              "tags": sort_tags(mbrel.get("tag-list", []))}

        if rg["id"] not in release_group_map:
            rg_artists, _ = artist_credits_to_artist_list(rg["artist-credit"])
            artists.update(rg_artists)
            release_group_map[rg["id"]] = {"artist_credit": rg["artist-credit-phrase"],
                                           "artists": sorted(rg_artists),
                                           "id": rg["id"],
                                           "last_updated": now,
                                           "first_release_date": rg.get("first-release-date"),
                                           "name": rg["title"], "tags": sort_tags(rg.get("tag-list", []))}

    return artists, release_map, release_group_map


def artist_credits_to_artist_list(credits):
    artists = set()
    artist_map = {}

    for item in credits:
        # Condition to skip join-phrase in multi-artists recordings
        if isinstance(item, dict):
            # Recording artist info
            artist_id = item["artist"]["id"]
            artist_name = item["artist"]["name"]
            tags = sort_tags(item["artist"].get("tag-list", []))

            artists.add(artist_id)
            if artist_id not in artist_map:
                artist_map[artist_id] = {"name": artist_name, "tags": tags}

    return list(artists), artist_map


def lookup_artists(artists):
    artist_map = {}
    for a in artists:
        mba = mb.get_artist_by_id(a, includes=["tags"])["artist"]
        artist_map[a] = {"name": mba["name"], "tags": sort_tags(mba.get("tag-list", []))}
    return artist_map


def scrape(query):
    mbid = query["mbid"]
    now = datetime.datetime.utcnow().isoformat()

    recording = mb.get_recording_by_id(mbid, includes=["artists", "tags"])["recording"]

    artists, artist_map = artist_credits_to_artist_list(recording["artist-credit"])

    data = {
        "mbid": recording["id"],
        "name": recording["title"],
        "artist_credit": recording["artist-credit-phrase"],
        "tags": sort_tags(recording.get("tag-list", [])),
        "artists": sorted(artists),
        "last_updated": now}

    # Get release names + tags + artists + release groups
    release_ids = get_releases_for_recording(mbid)
    other_artists, release_map, release_group_map = get_metadata_for_releases(release_ids, now)

    # For any artists in `other_artists` which are not in `artists`, look them up
    remaining_artists = list(set(other_artists) - set(artists))
    if remaining_artists:
        new_artist_map = lookup_artists(remaining_artists)
        artist_map.update(new_artist_map)

    data["artist_map"] = artist_map

    data["releases"] = sorted(release_ids)
    data["release_map"] = release_map
    data["release_group_map"] = release_group_map

    return data
