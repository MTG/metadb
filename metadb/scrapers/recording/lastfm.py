import urllib
import urllib2
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

    params = urllib.urlencode(params)
    request = urllib2.Request(LASTFM_API_ENDPOINT, params, headers)
    response = urllib2.urlopen(request).read()

    s = json.loads(response)
    if s.has_key('error'):
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

