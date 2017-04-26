import requests
from requests.adapters import HTTPAdapter
import json

TYPE = "recording"

sess = requests.Session()
adapter = HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
sess.mount("https://itunes.apple.com", adapter)


def config():
    pass


def dispose():
    pass


def do_itunes_lookup(artist, title):
    url = "https://itunes.apple.com/search"

    params = {"term": "{} {}".format(title.lower(), artist.lower()),
              "entity": "song"}

    headers = {"User-Agent": "curl/7.47.0"}
    r = sess.get(url, params=params, headers=headers)
    try:
        return r.json()
    except json.decoder.JSONDecodeError:
        # If there is no match, this will be an empty string
        content = r.content
        if len(content) == 0:
            return {}
        else:
            raise


def scrape(query):
    title = query.get("name")
    artist = query.get("artist_credit")
    if not title or not artist:
        return

    return do_itunes_lookup(artist, title)



