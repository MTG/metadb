import importlib


def create_scraper_object(scraper):
    modulepath = scraper["module"]
    package = importlib.import_module(modulepath)
    return package
