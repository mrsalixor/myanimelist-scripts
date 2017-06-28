from MALWork import Work
import Scrapper

import os
import time
import stat
import sys

import urllib.request
import json

class Manga(Work):
    READING_STATUSES = {1: "Reading", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to read"}
    MANGA_TYPES = {0: "Unknown", 1: "Manga", 2: "Light Novel", 3: "One-shot", 5: "Manhwa"}

    def __init__(self, manga_info_fromuserlist):
        id = int(manga_info_fromuserlist["series_mangadb_id"])
        super().__init__(manga_info_fromuserlist, id = id)

        self._chapters = manga_info_fromuserlist["series_chapters"]
        self._volumes = manga_info_fromuserlist["series_volumes"]


    def __str__(self):
        return "Manga#{} : {}".format(self.id, self.title)

    def workType(self):
        return self.MANGA_TYPES[self.type]


    def retrieveFullInfo(self):
        if self.id <= 0:
            print("Manga ID can't be negative or zero.", flush=True)
            return -1

        url = 'http://jikan.me/api/manga/{}'.format(self.id)
        os.makedirs('manga_caches', exist_ok=True)
        cache_filename = os.path.join('manga_caches', 'manga_{}.json'.format(self.id))

        self._data = Scrapper.retrieveJSONfromURL(url, destination=cache_filename)

        if self._data == {}:
            return -1
        else:
            return 1


    """ Number of chapters of a manga """
    @property
    def chapters(self):
        return self._chapters

    @chapters.setter
    def chapters(self, chapters):
        self._chapters = chapters

    @chapters.deleter
    def chapters(self):
        del self._chapters


    """ Number of volumes of a manga """
    @property
    def volumes(self):
        return self._volumes

    @volumes.setter
    def volumes(self, volumes):
        self._volumes = volumes

    @volumes.deleter
    def volumes(self):
        del self._volumes
