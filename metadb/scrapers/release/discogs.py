import json
import re
import discogs_client

DISCOGS_KEY = ""


class ApiException(Exception):
    pass


def config():
    pass


def dispose():
    pass


def parse_db_data(mbid, data, writer):
    if not data:
        print('{} nodata'.format(mbid), file=sys.stderr)
    for r in data:
        id = r['id']
        genre = r['genre']
        style = r['style']
        type = r['type']
        if genre:
            row = [mbid, id, type, 'genre']
            row.extend(genre)
            writer.writerow(row)
        if style:
            row = [mbid, id, type, 'style']
            row.extend(style)
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
