from MALAnime import Anime
from MALManga import Manga

import urllib.parse
import urllib.request

import xml.dom.minidom
import xmltodict

import sys

import time
import os
import stat

import csv

class User:
    LIST_REFRESH_DELAY = 3600

    def __init__(self, pseudo):
        self.pseudo = pseudo

        self.animes = set()
        self.mangas = set()

        self.anime_filename = self.pseudo + '_animelist'
        self.manga_filename = self.pseudo + '_mangalist'

        self.animes_watch_statuses = {}
        self.animes_scores = {}


    """ Retrieve the work's list of a user given the type of work """
    def retrieveWorkList(self, type, limit=15000000):
        if type != "anime" and type != "manga":
            sys.exit("Wrong work type")

        filename = self.anime_filename if type == "anime" else self.manga_filename

        if not self.checkWorkList(type):
            url = 'https://myanimelist.net/malappinfo.php?u=' + self.pseudo + '&status=all&type=' + type
            xml_info = urllib.request.urlopen(url)
            content = xml_info.read()
            xml_info.close()

            with open(filename, 'bw') as fd:
                print("Saving {} list for user {}".format(type, self.pseudo))
                fd.write(content)

        with open(filename, 'br') as fd:
            work_list = xmltodict.parse(fd.read())

        if(len(work_list["myanimelist"]) <= 1):
            print("Empty {} list for user {}".format(type, self.pseudo))
        else:
            for i in range(min(limit, len(work_list["myanimelist"][type]))):
                if type == "anime":
                    work = Anime(work_list["myanimelist"][type][i])
                if type == "manga":
                    work = Manga(work_list["myanimelist"][type][i])

                self.addWork(work, work_list["myanimelist"][type][i])

    def retrieveAnimeList(self, limit=999999):
        self.retrieveWorkList("anime", limit)

    def retrieveMangaList(self, limit=999999):
        self.retrieveWorkList("manga", limit)


    """ Check if a XML file corresponding to the work list of the user exists """
    def checkWorkList(self, type):
        filename = self.anime_filename if type == "anime" else self.manga_filename

        if os.path.isfile(filename):
            if time.time() - os.stat(filename)[stat.ST_MTIME] <= User.LIST_REFRESH_DELAY:
                return True
        return False


    """ Add a work to the user's list of animes or mangas """
    def addWork(self, work, work_info):
        if type(work) is Anime:
            self.animes.add(work)
        elif type(work) is Manga:
            self.mangas.add(work)
        else:
            print("Error while adding work to {}'s list'".format(self.pseudo))

        # TODO: make this more generic
        self.animes_watch_statuses[work] = work_info["my_status"]
        self.animes_scores[work] = work_info["my_score"]


    """ Return the list of shared animes between at least two users """
    def sharedAnime(*users):
        if(len(users) >= 2):
            anime_intersect = users[0].animes
            for user in users:
                anime_intersect = anime_intersect & user.animes
            return anime_intersect
        else:
            print("Not enough users were provided (2 required)")
            return set()


    """ Return the list of animes found between multiple users """
    def unionAnime(*users):
        if(len(users) >= 2):
            anime_union = users[0].animes
            for user in users:
                anime_union = anime_union | user.animes
            return anime_union
        else:
            print("Not enough users were provided (2 required)")
            return set()


    """ Save shared animes of multiple users to a .csv file """
    def toCSV(*users, destination = 'shared_anime_grid.csv', filetype = 'CSV'):
        if filetype == 'TSV':
            delimiter = '\t'
        else:
            delimiter = '|'

        if(len(users) >= 2):
            union_anime = User.unionAnime(*users)
            pseudos = [user.pseudo for user in users]
            pseudos.insert(0, '')

            pseudos_string = pseudos[1]
            for pseudo in pseudos[2:]:
                pseudos_string += ", " + pseudo


            with open(destination, 'w') as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(pseudos)

            with open(destination, 'ba') as f:
                for anime in union_anime: # Iterate over animes
                    row = anime.title
                    for user in users: # Iterate over users
                        row += delimiter

                        if anime in user.animes:
                            if user.animes_watch_statuses[anime] == '1' or user.animes_watch_statuses[anime] == '2':
                                row += str(user.animes_scores[anime])
                            elif user.animes_watch_statuses[anime] == '6':
                                row += 'P'
                            else:
                                row += 'X'

                    row += '\n'
                    f.write(row.encode("utf-8"))

            print("The {} file for users {} was generated".format(filetype, pseudos_string))
        else:
            print("Not enough users were provided (2 required)")


    """ Save shared animes of multiple users to a .tsv file """
    def toTSV(*users, destination = 'shared_anime_grid.tsv'):
        User.toCSV(*users, destination = destination, filetype = 'TSV')
