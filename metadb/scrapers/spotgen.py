import sys
import spotipy


sp = spotipy.Spotify()
sp.trace = False

def get_artist(name):
	results = sp.search(q='artist:' + name, type='artist')
	items = results['artists']['items']
	if len(items) > 0:
		return items[0]
	else:
		return None



def scrape(mbid, artist, title, metadata=None):
	data = None
	spot_artist = get_artist(artist)
	print('====', spot_artist['name'], '====')
	if len(spot_artist['genres']) > 0:
		print('Genres: ', ','.join(spot_artist['genres']))
		data = spot_artist['genres']

	if data:
		return data





