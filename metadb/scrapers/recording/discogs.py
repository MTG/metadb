import re
import discogs_client

TYPE = "recording"

DISCOGS_KEY = ""


def config():
    pass


def dispose():
    pass


class ApiException(Exception):
    pass


def scrape(query):

    mbid = query['mbid']
    artist = query['artist_credit']
    title = query['name']

    if not artist or not title:
        raise Exception("Artist and recording strings are required")
    print("Scraping recording information for", mbid, "-", artist, "-", title)

    title_simple = re.sub(r'\W+', '', title.lower())

    data = None  
    try:
        d = discogs_client.Client('AB_Discogs/0.1', user_token=DISCOGS_KEY)
        results = d.search(artist=artist, track=title)
        data = []
        #i = 0
        for r in results:
            #i += 1
            for t in r.tracklist:
                track_simple = re.sub(r'\W+', '',  t.data['title'].lower())
                #print i, track_simple, "-->", title_simple, "MATCH" if title_simple == track_simple else ""
                if title_simple == track_simple:
                    data.append(r.data)
                    break


    except ApiException as ex:
        raise

    if data:
        return data, TYPE

