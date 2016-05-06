import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json

LASTFM_KEY = ""
LASTFM_API_ENDPOINT = 'http://ws.audioscrobbler.com/2.0/'

class ApiException(Exception):
    pass

def query(method, **kwargs):
    params = dict(kwargs)
    params['method'] = method
    params['api_key'] = LASTFM_KEY
    params['format'] = 'json'

    headers = {
        'User-Agent': 'lastfmapi',
    }

    params = urllib.parse.urlencode(params)
    request = urllib.request.Request(LASTFM_API_ENDPOINT, params, headers)
    response = urllib.request.urlopen(request).read()

    s = json.loads(response)
    if 'error' in s:
        raise ApiException(s['message'])
    return s

def scrape(mbid, artist, title, metadata=None):
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

