import requests
import urllib.parse
from metadb import log

TYPE = "recording"

def do_itunes_lookup(artist, title):
    url = "https://itunes.apple.com/search"

    params = {"term": "{} {}".format(title.lower(), artist.lower()),
              "entity": "song"}

    headers = {"User-Agent": "curl/7.47.0"}
    r = requests.get(url, params, headers=headers)
    return r.json()


def scrape(query):
    title = query.get("recording")
    artist = query.get("artist")
    if not title or not artist:
        return

    return {"type": TYPE,
            "response": do_itunes_lookup(artist, title)}



