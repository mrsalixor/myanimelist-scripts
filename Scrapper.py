import os
import time
import stat

import urllib.request
import json


def retrieveJSONfromURL(url, destination="", cache_delay=0):
    cached = True

    # If the cache file does not exists, it means data hasn't been cached
    if destination != "":
        if not os.path.isfile(destination):
            cached = False
        # Check if the cache file has been refreshed in the interval of time provided
        else:
            if cache_delay > 0:
                cached = (time.time() - os.stat(destination)[stat.ST_MTIME] > cache_delay)

    # If data is not cached, we have to cache it once again
    if not cached and destination != "":
        try:
            print("Caching JSON data at {}".format(destination), flush=True)
            urllib.request.urlretrieve(url, destination)
        except urllib.error.HTTPError as err:
            print("Error {} when retrieveing JSON data.".format(err), flush=True)
            return {}
    else:
        print("Using cached JSON data at {}".format(destination), flush=True)

    # Read the cached data
    with open(destination, 'r', encoding="utf-8") as cache:
        data = json.load(cache)

    return data

def scrapWorks(start=0, delay=0, worktype=''):
    if not worktype or worktype != 'manga' or worktype != 'anime':
        return

    for i in range(start, 500000):
        url = 'http://jikan.me/api/{}/{}'.format(worktype, i)
        os.makedirs('{}_caches'.format(worktype), exist_ok=True)
        cache_filename = os.path.join('{}_caches'.format(worktype), '{}_{}.json'.format(worktype, i))

        data = retrieveJSONfromURL(url, destination=cache_filename, cache_delay=delay)

        if not data:
            continue

def scrapAnimes(start=0, delay=0):
    scrapWorks(start, delay, 'anime')

def scrapMangas(start=0, delay=0):
    scrapWorks(start, delay, 'manga')
