import requests
from requests.adapters import HTTPAdapter

LASTFM_KEY = ""
LASTFM_API_ENDPOINT = 'http://ws.audioscrobbler.com/2.0/'

sess = requests.Session()
adapter = HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
sess.mount(LASTFM_API_ENDPOINT, adapter)


class ApiException(Exception):
    pass


def config():
    pass


def dispose():
    pass


def query(method, **kwargs):
    params = dict(kwargs)
    params["method"] = method
    params["api_key"] = LASTFM_KEY
    params["format"] = "json"

    headers = {
        "User-Agent": "lastfmapi",
    }

    r = sess.get(LASTFM_API_ENDPOINT, params=params, headers=headers)
    s = r.json()
    if "error" in s:
        raise ApiException(s["message"])
    return s


def scrape(meta):
    artist = meta["artist_credit"]
    title = meta["name"]

    data = None
    # Since the new lastfm website was released, mbid
    # lookup is unreliable
    # data = query("track.getTopTags", mbid=mbid)
    try:
        data = query("track.getTopTags", track=title, artist=artist)
    except ApiException as ex:
        raise

    if data:
        return data

