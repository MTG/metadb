import requests
from requests.adapters import HTTPAdapter

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
    return r.json()


def scrape(query):
    title = query.get("recording")
    artist = query.get("artist")
    if not title or not artist:
        return

    return {"type": TYPE,
            "response": do_itunes_lookup(artist, title)}



