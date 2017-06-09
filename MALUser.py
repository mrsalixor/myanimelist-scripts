from MALAnime import Anime
from MALManga import Manga

import urllib.parse
import urllib.request

import xml.dom.minidom
import xmltodict

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


    """ Retrieve the anime list of a user """
    def retrieveAnimeList(self, limit=15000000, status='all'):
        if not self.checkAnimeList():
            url = 'https://myanimelist.net/malappinfo.php?u=' + self.pseudo + '&status=all&type=anime'
            xml_info = urllib.request.urlopen(url)
            content = xml_info.read()
            xml_info.close()

            with open(self.anime_filename, 'bw') as file:
                print("Saving anime list for user {}".format(self.pseudo))
                file.write(content)

        with open(self.anime_filename, 'br') as animelist_file:
            anime_list = xmltodict.parse(animelist_file.read())

        for i in range(min(limit, len(anime_list["myanimelist"]["anime"]))):
            anime = Anime(anime_list["myanimelist"]["anime"][i])
            self.addWork(anime, anime_list["myanimelist"]["anime"][i])


    """ Check if a XML file corresponding to the anime list of the user exists """
    def checkAnimeList(self):
        if os.path.isfile(self.anime_filename):
            if time.time() - os.stat(self.anime_filename)[stat.ST_MTIME] <= User.LIST_REFRESH_DELAY:
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
