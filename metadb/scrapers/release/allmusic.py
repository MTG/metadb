import requests
import json
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
import yaml

session = requests.Session()
adapter = HTTPAdapter(max_retries=5, pool_connections=100, pool_maxsize=100)
session.mount("http://www.allmusic.com", adapter)

session_cookies = {}
DATA = {}

def config():
    pass


def dispose():
    pass


def config_dump(data_file):
    GENRE_TREE = yaml.load(open(data_file))
    DATA["GENRE_TREE"] = GENRE_TREE
    GENRE_TREE_paths = styles(GENRE_TREE)
    DATA["GENRE_TREE_paths"] = GENRE_TREE_paths
    GENRE_TREE_styles = [p[-1] for p in GENRE_TREE_paths]
    DATA["GENRE_TREE_styles"] = set(GENRE_TREE_styles)


def styles(tree):
    styles = []
    for g, child in tree.items():
        if isinstance(child, list):
            for gs in child:
                if isinstance(gs, str):
                    styles.append((g, gs))
                if isinstance(gs, dict):
                    for gss, gsschild in gs.items():
                        for gsss in gsschild:
                            styles.append((g, gss, gsss))
        elif type(child) is dict:
            for gs, gschild in child.items():
                for gss in gschild:
                    styles.append((g, gs, gss))
        else:
            raise Exception("Unexpected genre tree format")
    return styles


def extract_style(styles, genres):
    results = []

    genre_set = set(genres)
    for s in styles:
        if s not in DATA["GENRE_TREE_styles"]:
            continue

        matched = False
        for style_path in DATA["GENRE_TREE_paths"]:
            if s == style_path[-1] and style_path[0] in genre_set:
                results.append(style_path)
                matched = True

    # We want to add all genres of a style, even if they aren't
    # explicitly listed
    all_genres = genre_set | set([r[0] for r in results])
    results += [(g,) for g in all_genres]
    return results


def parse_db_data(mbid, data, writer):

    album = data["album"]
    if album:
        genres = album["genres"]
        styles = album["styles"]

        if not genres:
            return

        # only use 1st and 2nd level genres
        annotations = []
        for a in extract_style(styles, genres):
            if len(a) == 0:
                continue
            elif len(a) == 2 or len(a) == 1:
                annotations.append(a)
            elif len(a) == 3:
                annotations.append((a[0], a[1]))
                annotations.append((a[0], a[2]))

        # remove duplicates that might occur after extracting only 2nd level subgenres
        annotations = list(set(annotations))
        annotations = ["---".join(list(a)).lower() for a in annotations]

        if annotations:
            if not isinstance(mbid, list):
                mbid = [mbid]

            for m in mbid:
                row = [m] + sorted(annotations)
                writer.writerow(row)


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

