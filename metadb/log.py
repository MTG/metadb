import logging

import logging
logfmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

lookuplog = logging.Logger('lookup')
ch = logging.StreamHandler()
ch.setFormatter(logfmt)
lookuplog.setLevel(logging.INFO)
lookuplog.addHandler(ch)

def info(*args, **kwargs):
    lookuplog.info(*args, **kwargs)
