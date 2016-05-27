import requests
import os
import sys
import json
import errno
from bs4 import BeautifulSoup
import time
import random

from metadb import util
from metadb import log

TYPE = "release"

def _get_cookies():
    r = requests.get("http://www.allmusic.com/")
    return r.cookies

def scrape(query):
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
        relres = get_first_release(searchres)
        release = parse_release(relres)
        data["album"] = release

    return {"type": TYPE, "data": data}

def get_first_release(data):
    if data:
        rel = data[0]
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
    cookies, headers = query_data()
    r = requests.get(url, headers=headers, cookies=cookies)
    return r.content

def search(artist, release):
    cookies, headers = query_data()
    r = requests.get('http://www.allmusic.com/search/albums/{} {}'.format(artist, release), headers=headers, cookies=cookies)
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
    cookies = {
        '_gat': '1',
        '__qca': 'P0-559467384-1457973982414',
        '_gat_cToolbarTracker': '1',
        'bm_monthly_unique': 'true',
        'bm_daily_unique': 'true',
        'bm_sample_frequency': '1',
        'policy': 'notified',
        'registration_prompt': '3',
        'allmusic_session': 'a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%2268b730334cd74b640a5b17dd563b2b61%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A18%3A%222607%3Af700%3A1%3A83%3A%3A92%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A120%3A%22Mozilla%2F5.0+%28Macintosh%3B+Intel+Mac+OS+X+10_11_3%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F50.0.2661.18+Safari%2F537.36%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1457973975%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A4%3A%22user%22%3Bi%3A0%3B%7D426c4443986a9d499e0956f67c107ae7776f09c9',
        '_ga': 'GA1.2.1178384982.1457973977',
        'ads_bm_last_load_status': 'NOT_BLOCKING',
        'bm_last_load_status': 'NOT_BLOCKING',
        'OX_plg': 'pm',
    }

    headers = {
        'DNT': '1',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-NZ,en;q=0.8,es;q=0.6',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.18 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'http://www.allmusic.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    return cookies, headers

