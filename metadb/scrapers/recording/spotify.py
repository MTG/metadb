import spotipy

sp = spotipy.Spotify()


def config():
    pass


def dispose():
    pass


def get_artist(name):
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None


def scrape(query):
    mbid = query['mbid']
    artist = query['artist_credit']
    title = query['name']

    data = None
    spot_artist = get_artist(artist)
    if len(spot_artist['genres']) > 0:
        data = spot_artist['genres']

    if data:
        return data
