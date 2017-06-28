from MALAnime import Anime
from MALManga import Manga
from MALWork import Work

import urllib.parse
import urllib.request

import xml.dom.minidom
import xmltodict

import sys

import time
import os
import stat

import csv

from PIL import Image

import requests
from io import BytesIO
from base64 import b16encode

class User:
    LIST_REFRESH_DELAY = 3600 #1 hour
    AVATAR_REFRESH_DELAY = 7200 #2 hours

    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.userid = 0

        self.works = {} # (id, worktype): work
        self.work_informations = {} # work: (score, status)

        path = "animelists"
        if not os.path.isdir(path): os.makedirs(path)
        self.anime_filename = os.path.join(path, self.pseudo + '_animelist')

        path = "mangalists"
        if not os.path.isdir(path): os.makedirs(path)
        self.manga_filename = os.path.join(path, self.pseudo + '_mangalist')


    """ Retrieve the work's list of a user given the type of work """
    def retrieveWorkList(self, type):
        if type != "anime" and type != "manga":
            sys.exit("Wrong work type")

        filename = self.anime_filename if type == "anime" else self.manga_filename

        # If the workfile was not refreshed for the given interval of time
        if not self.checkWorkList(type):
            url = 'https://myanimelist.net/malappinfo.php?u=' + self.pseudo + '&status=all&type=' + type
            xml_info = urllib.request.urlopen(url)
            content = xml_info.read()
            xml_info.close()

            if(content == b'<?xml version="1.0" encoding="UTF-8" ?><myanimelist></myanimelist>'):
                print("The user {} does not seem to exist".format(self.pseudo), flush=True)
                return -1

            with open(filename, 'bw') as fd:
                print("Saving {} list for user {}".format(type, self.pseudo), flush=True)
                fd.write(content)

        # Open the workfile for that user and parse it
        with open(filename, 'br') as fd:
            work_list = xmltodict.parse(fd.read())

        self.pseudo = work_list["myanimelist"]["myinfo"]["user_name"]
        self.userid = work_list["myanimelist"]["myinfo"]["user_id"]

        # If there's no work for the user
        if len(work_list["myanimelist"]) <= 1:
            print("Empty {} list for user {}".format(type, self.pseudo), flush=True)
            return -2

        # Store the works, scores and statuses for this user
        for i in range(len(work_list["myanimelist"][type])):
            if type == "anime":
                work = Anime(work_list["myanimelist"][type][i])
            if type == "manga":
                work = Manga(work_list["myanimelist"][type][i])

            score = int(work_list["myanimelist"][type][i]["my_score"])
            status = int(work_list["myanimelist"][type][i]["my_status"])

            self.work_informations[work] = (score, status)
            self.works[(work.id, type)] = work

        return 0

    def retrieveAnimeList(self):
        return self.retrieveWorkList("anime")

    def retrieveMangaList(self):
        return self.retrieveWorkList("manga")


    """ Check if a XML file corresponding to the work list of the user exists """
    def checkWorkList(self, type):
        filename = self.anime_filename if type == "anime" else self.manga_filename

        if os.path.isfile(filename):
            if time.time() - os.stat(filename)[stat.ST_MTIME] <= User.LIST_REFRESH_DELAY:
                return True
        return False


    """ Return the list of works found between multiple users """
    def joinedWorks(*users):
        if len(users) < 2:
            print("Not enough users were provided (2 required)", flush=True)
            return {}

        work_union = {}
        for user in users:
            work_union.update(user.works)
        return work_union


    """ Return the list of works found between multiple users and the stats """
    def joinedWorksWithStats(users, worktype, id = 0, title=""):
        if len(users) < 2:
            print("Not enough users were provided (2 required)", flush=True)
            return {}

        title = title.lower()
        work_union = {}
        already_found = False

        for user in users:
            for work in list(user.works.values()):
                # If this work is not of the correct type, skip it
                if (worktype == 'anime' and type(work) is Manga) or (worktype == 'manga' and type(work) is Anime):
                    continue

                # Split the alternative titles
                alt_titles = []
                if not work.alt_titles is None:
                    alt_titles = work.alt_titles.split("; ")

                # Filter by id
                if id != 0 and id != work.id:
                    continue

                # Filter by title or alternative title
                if title != "":
                    found = False
                    exact = False
                    for alt_title in alt_titles:
                        if alt_title != "":
                            found = found or title in alt_title.lower()
                            exact = exact or title == alt_title.lower()
                    found = found or title in work.title.lower()
                    exact = exact or title == work.title.lower()

                    # If the title matches exactly, only keep this row
                    if exact:
                        already_found = True
                        tmp = {}
                        if work in work_union:
                            tmp = work_union[work]
                        work_union = {}
                        work_union[work] = tmp
                        work_union[work].update({user.pseudo.lower(): user.work_informations[work]})
                        break

                    # If the title does not match, we skip to the next work
                    if not found:
                        continue

                # We add the work in our final list
                if not already_found:
                    if not work in work_union:
                        work_union[work] = {}
                    work_union[work].update({user.pseudo.lower(): user.work_informations[work]})

        return work_union


    """ Save shared works of multiple users to a .csv file """
    def toCSV(users, destination = 'shared_works.csv', filetype = 'CSV', worktype='anime'):
        delimiter = '\t' if (filetype == 'TSV') else '|'

        if len(users) < 2:
            print("Not enough users were provided (2 required)", flush=True)
            return -1

        joined_works = User.joinedWorks(*users)
        pseudos = [user.pseudo for user in users]
        pseudos_string = ", ".join(pseudos)

        with open(destination, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(pseudos)

            # We iterate over the works that every users share
            for key, work in joined_works.items():
                # If this work is not of the correct type, skip it
                if (worktype == 'anime' and type(work) is Manga) or (worktype == 'manga' and type(work) is Anime):
                    continue

                row = []
                row.append(work.id)
                row.append(work.title)
                row.append(work.workType())
                row.append(work.poster)

                # Iterate over users and fill the CSV file
                for user in users:
                    if work in list(user.works.values()):
                        if user.work_informations[work][1] == 1 or user.work_informations[work][1] == 2:
                            row.append(user.work_informations[work][0])
                        elif user.work_informations[work][1] == 3:
                            row.append('O')
                        elif user.work_informations[work][1] == 4:
                            row.append('D')
                        else:
                            row.append('P')
                    else:
                        row.append('')

                writer.writerow(row)

        print("The {} {} file for users {} was generated".format(worktype, filetype, pseudos_string), flush=True)
        return 0


    """ Save shared works of multiple users to a .tsv file """
    def toTSV(*users, destination = 'shared_works.tsv', worktype='anime'):
        User.toCSV(*users, destination = destination, filetype = 'TSV', worktype=worktype)


    """ Returns a sorted list of (genres, count) for animes or mangas found in this user's list """
    def favoriteGenre(self, worktype, limit=5):
        genre_count = {}
        genre_names = {}

        for key, work in self.works.items():
            # If this work is not of the correct type, skip it
            if (worktype == 'anime' and type(work) is Manga) or (worktype == 'manga' and type(work) is Anime):
                continue

            retrieve_status = work.retrieveFullInfo()
            if retrieve_status < 0:
                break

            for genre_id, genre_name in work.genres:
                genre_count[genre_id] = 0 if not genre_id in genre_count else genre_count[genre_id]+1
                genre_names[genre_id] = '' if not genre_id in genre_names else genre_name

        final = {genre_names[key]: genre_count[key] for key in genre_count}
        return sorted(final.items(), key=lambda x: x[1], reverse=True)[0:min(limit, len(final)-1)]


    """ Returns a sorted list of (studio, count) for animes found in this user's list """
    def favoriteStudio(self, limit=5):
        studio_count = {}
        studio_names = {}

        for key, work in self.works.items():
            # If this work is not of the correct type, skip it
            if not type(work) is Anime:
                continue

            retrieve_status = work.retrieveFullInfo()
            if retrieve_status < 0:
                break

            for studio_id, studio_name in work.studios:
                studio_count[studio_id] = 0 if not studio_id in studio_count else studio_count[studio_id]+1
                studio_names[studio_id] = '' if not studio_id in studio_names else studio_name

        final = {studio_names[key]: studio_count[key] for key in studio_count}
        return sorted(final.items(), key=lambda x: x[1], reverse=True)[0:min(limit, len(final)-1)]


    """ Save the user's avatar for a given period of time """
    def saveAvatar(self):
        avatar_url = "https://myanimelist.cdn-dena.com/images/userimages/{}.jpg".format(self.userid)
        avatar_local = os.path.join('avatars', '{}.jpg'.format(self.userid))

        os.makedirs('avatars', exist_ok=True)

        should_retrieve = True
        if os.path.isfile(avatar_local):
            if time.time() - os.stat(avatar_local)[stat.ST_MTIME] <= User.AVATAR_REFRESH_DELAY:
                should_retrieve = False

        if should_retrieve:
            response = requests.get(avatar_url)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(avatar_local)

        shorter_side = min(img.size)
        img_crop = img.crop( (0, 0, shorter_side, shorter_side) )

        img_crop.save(avatar_local)
        return avatar_local
