import requests
import json
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

session = requests.Session()
adapter = HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
session.mount("http://www.allmusic.com", adapter)

session_cookies = {}


def config():
    pass


def dispose():
    pass


def parse_db_data(mbid, data, writer):

    album = data["album"]
    if album:
        genres = album["genres"]
        styles = album["styles"]

        if genres:
            row = [mbid, "genre"]
            row.extend(genres)
            writer.writerow(row)
        if styles:
            row = [mbid, "style"]
            row.extend(styles)
            writer.writerow(row)
    else:
        print("{} nodata".format(mbid), file=sys.stderr)



def _get_cookies():
    headers = query_data()
    r = session.get("http://www.allmusic.com/", headers=headers)
    session_cookies['allmusic_session'] = r.cookies.get('allmusic_session')


def scrape(query):
    if not session_cookies:
        _get_cookies()

    mbid = query['mbid']
    artist = query['artist']
    release = query['release']
    year = query['year']

    if not artist or not release or not year:
        raise Exception("Artist, release, and year information is required. Query: %s" % json.dumps(query))
    print("Scraping recording information for", mbid + ":", artist, "-", release, "-", year)

    if year:
        year = year[:4]

    res = search(artist, release)
    data = {}
    searchres = parse_search(res, artist, release)

    data["search_results"] = searchres
    data["album"] = {}
    if searchres:
        relres = get_first_release(searchres, year)
        if relres:
            release = parse_release(relres)
            data["album"] = release

        return data
    else:
        # No search results, return empty data
        return {}



def get_first_release(data, year):
    if data:
        if year:
            filtered = [d for d in data if d["year"] == year]
            if filtered:
                data = filtered
        rel = data[0]
        albumdata = rel["albumdata"]
        if albumdata:
            releaseurl = rel["albumdata"].get("href")
            if releaseurl:
                content = load_release(releaseurl)
                return content
    return {}


def parse_release(data):
    s = BeautifulSoup(data, "html5lib")

    genrenode = s.find("div", {"class": "genre"})
    stylenode = s.find("div", {"class": "styles"})
    moodnode = s.find("section", {"class": "moods"})
    themenode = s.find("section", {"class": "themes"})

    genres = []
    if genrenode:
        for a in genrenode.find_all("a"):
            genres.append(a.text.strip())
    styles = []
    if stylenode:
        for a in stylenode.find_all("a"):
            styles.append(a.text.strip())
    moods = []
    if moodnode:
        for a in moodnode.find_all("a"):
            moods.append(a.text.strip())
    themes = []
    if themenode:
        for a in themenode.find_all("a"):
            themes.append(a.text.strip())

    review = s.find("section", {"class": "review"})
    if review:
        review = review.text

    return {"genres": genres, "styles": styles, "moods": moods, "themes": themes, "review": review}


def load_release(url):
    headers = query_data()
    r = session.get(url, headers=headers, cookies=session_cookies)
    return r.content


def search(artist, release):
    headers = query_data()
    r = session.get('http://www.allmusic.com/search/albums/{} {}'.format(artist, release), headers=headers, cookies=session_cookies)
    return r.content


def parse_search(data, artist, release):
    s = BeautifulSoup(data, "html5lib")
    infos = s.find_all("div", {"class": "info"})
    data = []
    referrer = 'http://www.allmusic.com/search/albums/{} {}'.format(artist, release)
    for i in infos:
        title = i.find("div", {"class": "title"})
        if title:
            title = title.text.strip()
        artist = i.find("div", {"class": "artist"})
        if artist:
            artist = artist.text.strip()
        year = i.find("div", {"class": "year"})
        if year:
            year = year.text.strip()
        genres = i.find("div", {"class": "genre"})
        if genres:
            genres = genres.text.strip()
        artistnode = i.find("div", {"class": "artist"})
        artistdata = {}
        if artistnode:
            artistdata = artistnode.find("a")
            if artistdata:
                artistdata = artistdata.attrs
        albumnode = i.find("div", {"class": "title"})
        if albumnode:
            albumdata = albumnode.find("a")
            if albumdata:
                albumdata = albumdata.attrs
        data.append({"title": title, "artist": artist,
                     "year": year, "genres": genres,
                     "artistdata": artistdata, "albumdata": albumdata})
    return data


def query_data():
    headers = {
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-NZ,en;q=0.8,es;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.18 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'http://www.allmusic.com/',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    return headers

