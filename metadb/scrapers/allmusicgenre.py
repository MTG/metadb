# All Music genre
# Parse the genre tree from All Music

# http://www.allmusic.com/genres

import requests
from bs4 import BeautifulSoup
import yaml

import logging
log = logging.Logger(__name__)
ch = logging.StreamHandler()
logfmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(logfmt)
log.setLevel(logging.INFO)
log.addHandler(ch)

def main():
    content = get_content()
    yaml.safe_dump(content, open("allmusic-genres.yaml", "w"), default_flow_style=False)

def is_genre_tag(tag):
    if tag.has_attr("class"):
        cl = tag.attrs["class"]
        if "genre-parent" in cl or "genre-links" in cl:
            if tag.parent.parent.name == "ul" and "subgenres" in tag.parent.parent.attrs["class"]:
                return True
    return False

def parse_genre(name, url):
    urlpart = url.replace("http://www.allmusic.com/", "")
    log.info("%s: %s", name, url)
    soup = query(urlpart)
    subgenres = soup.find_all(is_genre_tag)

    genre = {}

    for sub in subgenres:
        if sub:
            title = sub.text.strip()
            styles = sub.parent.find_all("a", {"class": "genre-links"})
            style_names = [s.text.strip() for s in styles]
            genre[title] = style_names

    if not genre:
        # If we don't have anything yet, it's probably just a
        # single-layer genre list (Vocals)
        mappings = soup.find("section", {"class": "mapping"})
        genre = []
        if mappings:
            styles = mappings.find_all("a")
            for s in styles:
                s = s.text.strip()
                genre.append(s)

    return genre

def get_content():
    soup = query("genres")
    genres = soup.find_all("div", {"class": "genre"})
    genre_map = {}
    for g in genres:
        genre_name = g.h2.a.text.strip()
        genre_url = g.h2.a.attrs["href"]
        genre_map[genre_name] = parse_genre(genre_name, genre_url)

    return genre_map

def query(url):
    cookies = {
	'policy': 'notified',
	'registration_prompt': 'true',
	'allmusic_session': 'a%3A6%3A%7Bs%3A10%3A%22session_id%22%3Bs%3A32%3A%22436ea2391bb870cdbe50250de368934e%22%3Bs%3A10%3A%22ip_address%22%3Bs%3A18%3A%222607%3Af700%3A1%3A83%3A%3A92%22%3Bs%3A10%3A%22user_agent%22%3Bs%3A104%3A%22Mozilla%2F5.0+%28X11%3B+Linux+x86_64%29+AppleWebKit%2F537.36+%28KHTML%2C+like+Gecko%29+Chrome%2F49.0.2623.87+Safari%2F537.36%22%3Bs%3A13%3A%22last_activity%22%3Bi%3A1462864572%3Bs%3A9%3A%22user_data%22%3Bs%3A0%3A%22%22%3Bs%3A4%3A%22user%22%3Bi%3A0%3B%7D4249caad9ccd17c195126f2564a112906bdcb6ef',
    }

    headers = {
	'DNT': '1',
	'Accept-Encoding': 'gzip, deflate, sdch',
	'Accept-Language': 'en-US,en;q=0.8,es;q=0.6,ca;q=0.4,fr-CA;q=0.2,fr;q=0.2',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Referer': 'http://www.allmusic.com/',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
    }

    url = "http://www.allmusic.com/{}".format(url)
    r = requests.get(url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(r.content, "html5lib")
    return soup

if __name__ == "__main__":
    main()
