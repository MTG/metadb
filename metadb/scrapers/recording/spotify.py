import spotipy

def get_artist(name):
    sp = spotipy.Spotify()
    sp.trace = False
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None


def scrape(mbid, artist, title, metadata=None):
    data = None
    spot_artist = get_artist(artist)
    if len(spot_artist['genres']) > 0:
        data = spot_artist['genres']

    if data:
        return data
