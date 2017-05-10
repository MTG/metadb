import json
import re
import discogs_client
import sys
import yaml

DISCOGS_KEY = ""

DATA = {}

class ApiException(Exception):
    pass


def config():
    pass


def dispose():
    pass


def config_dump(data_filename):
    # we use DATA so that we don't have to use global
    GENRE_TREE = yaml.load(open(data_filename))
    DATA["GENRE_TREE"] = GENRE_TREE
    DATA["GENRE_TREE_styles"] = set([s for g in GENRE_TREE for s in GENRE_TREE[g]])


def extract_style(styles, genres):
    # find a parent genre among genres for each style in styles
    result = []
    for s in list(set(styles)):
        # Fix a style that was renamed by Discogs at some point in time
        s = s.replace("Shoegazer", "Shoegaze")

        #if s not in DATA["GENRE_TREE_styles"]:
        #   print("Unknown style: {}".format(s))

        matched = False
        for g in genres:
            if s in DATA["GENRE_TREE"][g]:
                result.append([g, s])
                matched = True
        #if not matched:
        #    print("Could not match {} to {}".format(s, genres))

    return result


def parse_db_data(mbid, data, writer):
    if not data:
        print('{} nodata'.format(mbid), file=sys.stderr)

    first = data[0]
    genres = first['genre']
    styles = first['style']

    if styles:
        styles = extract_style(styles, genres)

    genres_with_no_styles = set(genres) - set([g for g, s in styles])
    data = styles + [[g] for g in genres_with_no_styles]

    data = ["---".join(list(d)).lower() for d in data]

    if not isinstance(mbid, list):
        mbid = [mbid]

    for m in mbid:
        row = [m] + data
        writer.writerow(row)


def scrape(query):

    mbid = query['mbid']
    artist = query['artist']
    release = query['release']
    year = query['year']

    if not artist or not release or not year:
        raise Exception("Artist, release, and year information is required. Query: %s" % json.dumps(query))
    print("Scraping recording information for", mbid + ":", artist, "-", release, "-", year)

    release_simple = re.sub(r'\W+', '', release.lower())
    year = year.split('-')[0]

    data = None
    try:
        d = discogs_client.Client('AB_Discogs/0.1', user_token=DISCOGS_KEY)
        results = d.search(artist=artist, release_title=release)

        data = [r.data for r in results if 'year' in r.data and r.data['year']==year]

    except ApiException as ex:
        raise

    return data
