# Rate Your Music genre
# Parse the genre tree from Rate Your Music

# http://rateyourmusic.com/rgenre/

import requests
from bs4 import BeautifulSoup
import yaml

def main():
    content = get_content()
    data = parse_top_level(content)

    y = []
    for g in data:
        y.append(recurse_to_yaml(g))
    yaml.safe_dump(y, open("rym-genres.yaml", "w"), default_flow_style=False)

def recurse_to_yaml(node):
    if node.get("children", []):
        children = []
        for c in node["children"]:
            children.append(recurse_to_yaml(c))
        return {node["name"]: children}
    else:
        return node["name"]

def get_content():
    r = requests.get("http://rateyourmusic.com/rgenre/")
    soup = BeautifulSoup(r.content, "html.parser")
    content = soup.find("div", {"id": "content"})
    return content


def parse_top_level(content):

    genres = []
    for c in content.find_all(True, recursive=False):
        if c.name == "a" and c.attrs.get("class") == ["genre"]:
            genres.append(genre_tag_to_dict(c))
        elif c.name == "div" and c.attrs.get("style") == genreblockstyle:
            genres.append(parse_genre_with_subgenre(c))

    return genres


genreblockstyle = "background:#f8f8f8;border:#bbb 1px solid;padding:6px;margin:10px; "

def genre_tag_to_dict(tag):
    return {"name": tag.text,
            "href": tag.attrs["href"],
            "title": tag.attrs["title"]}

def parse_genre_with_subgenre(block):
    # This is a genre in bold with subgenres in a <blockquote>
    # a subgenre might be standalone, or it could have its own
    # subgenres (in which case we should recurse)
    genrename = block.select_one("b > a.genre")
    ret = genre_tag_to_dict(genrename)

    bq = block.find_next("blockquote")
    children = []
    for c in bq.find_all(True, recursive=False):
        if c.name == "a" and c.attrs.get("class") == ["genre"]:
            children.append(genre_tag_to_dict(c))
        elif c.name == "div" and c.attrs.get("style") == genreblockstyle:
            children.append(parse_genre_with_subgenre(c))
    ret["children"] = children
    return ret

if __name__ == "__main__":
    main()
