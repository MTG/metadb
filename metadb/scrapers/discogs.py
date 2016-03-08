import json
import re
import discogs_client
import time

DISCOGS_KEY = ""

class ApiException(Exception):
    pass


def scrape(mbid, artist, title, metadata=None):
    title_simple = re.sub(r'\W+', '', title.lower())

    data = None  
    try:
        d = discogs_client.Client('AB_Discogs/0.1', user_token="qnySAoSOYusdpbAvSvbXDnSqMyzgpATQqTLlnklk")
        results = d.search(artist=artist, track=title)
        data = []
        #i = 0
        print results.count
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
        return data

