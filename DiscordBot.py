import discord
import asyncio

import csv
import urllib.request
import os
import sys
import time
import stat

from PIL import Image

import requests
from io import BytesIO
from base64 import b16encode

from MALUser import User

client = discord.Client()

@client.event
async def on_ready():
    print('---------------------------------', flush=True)
    print('Logged in as : {}'.format(client.user.name), flush=True)
    print('Client ID : {}'.format(client.user.id), flush=True)
    print('---------------------------------', flush=True)

    await client.change_presence(game=discord.Game(name='!help'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # HELP : !help

    if message.content.lower().startswith('!help'):
        msg = "```!anime_stats <user1,...,userN> <id/title> : scores and statuses of users for a given anime\n"
        msg += "!manga_stats <user1,...,userN> <id/title> : scores and statuses of users for a given manga\n"
        msg += "!anime_favgenre <user> : favorite anime genres for an user\n"
        msg += "!manga_favgenre <user> : favorite manga genres for an user\n"
        msg += "!favstudios <user> : favorite anime studios for an user```"
        await client.send_message(message.channel, msg)


    # FAVORITE ANIME STUDIO : !favstudios <user>

    if message.content.lower().startswith('!favstudios'):
        message_split = message.content.split(" ", 1)

        if len(message_split) != 2:
            msg = '{0.author.mention}, please type `!favstudios <user>`.'.format(message, worktype)
            await client.send_message(message.channel, msg)
            return

        username = message_split[1].strip()

        # Temporary message while working the request
        msg = '{0.author.mention}, currently retrieving data from MyAnimeList. Please wait !'.format(message)
        tmp = await client.send_message(message.channel, msg)

        user = User(username)
        if user.retrieveWorkList('anime') == -1:
            msg = '{0.author.mention}, this user does not seem to exist.'.format(message)
            await client.edit_message(tmp, msg)
            return

        studios = user.favoriteStudio(limit=10)
        description = ""
        title = "{}'s favorite anime studios".format(user.pseudo)

        for studio_name, studio_count in studios:
            description += "**{}:** {} animes\n".format(studio_name, studio_count)

        user_url = "https://myanimelist.net/profile/{}".format(user.pseudo)
        avatar_url = "https://myanimelist.cdn-dena.com/images/userimages/{}.jpg".format(user.userid)
        color = get_main_color(avatar_url)

        result = discord.Embed(title=title, description=description, url=user_url, color=color)
        result.set_thumbnail(url=avatar_url)
        msg = '{0.author.mention}, here are the results for your request : '.format(message)
        await client.edit_message(tmp, msg, embed=result)


    # FAVORITE ANIME OR MANGA GENRES : !anime_favgenre <user> OR !manga_favgenre <user>

    if message.content.lower().startswith('!anime_favgenre') or message.content.lower().startswith('!manga_favgenre'):
        if message.content.lower().startswith('!anime_favgenre'):
            worktype = 'anime'
        elif message.content.lower().startswith('!manga_favgenre'):
            worktype = 'manga'
        else:
            return

        message_split = message.content.split(" ", 1)

        if len(message_split) != 2:
            msg = '{0.author.mention}, please type `!{1}_favgenre <user>`.'.format(message, worktype)
            await client.send_message(message.channel, msg)
            return

        username = message_split[1].strip()

        # Temporary message while working the request
        msg = '{0.author.mention}, currently retrieving data from MyAnimeList. Please wait !'.format(message)
        tmp = await client.send_message(message.channel, msg)

        user = User(username)
        if worktype == 'anime' or worktype == 'manga':
            if user.retrieveWorkList(worktype) == -1:
                msg = '{0.author.mention}, this user does not seem to exist.'.format(message)
                await client.edit_message(tmp, msg)
                return
        else:
            msg = '{0.author.mention}, something went wrong.'.format(message)
            await client.edit_message(tmp, msg)
            return

        genres = user.favoriteGenre(worktype, limit=10)
        description = ""
        title = "{}'s favorite {} genres".format(user.pseudo, worktype)

        for genre_name, genre_count in genres:
            description += "**{}:** {} {}\n".format(genre_name, genre_count, worktype+"s")

        user_url = "https://myanimelist.net/profile/{}".format(user.pseudo)
        avatar_url = "https://myanimelist.cdn-dena.com/images/userimages/{}.jpg".format(user.userid)
        color = get_main_color(avatar_url)

        result = discord.Embed(title=title, description=description, url=user_url, color=color)
        result.set_thumbnail(url=avatar_url)
        msg = '{0.author.mention}, here are the results for your request : '.format(message)
        await client.edit_message(tmp, msg, embed=result)


    # ANIME OR MANGA STATS : !anime_stats <user1,...,userN> <id/title> OR !manga_stats <user1,...,userN> <id/title>

    if message.content.lower().startswith('!anime_stats') or message.content.lower().startswith('!manga_stats'):
        if message.content.lower().startswith('!anime_stats'):
            worktype = 'anime'
        elif message.content.lower().startswith('!manga_stats'):
            worktype = 'manga'
        else:
            return

        message_split = message.content.split(" ", 2)

        if len(message_split) != 3:
            msg = '{0.author.mention}, please type `!{1}_stats <user1,...,userN> <id/title>`.'.format(message, worktype)
            await client.send_message(message.channel, msg)
            return

        search = message_split[2].strip()
        search_id = 0
        search_title = ""

        if not search.isnumeric():
            search_title = search
        else:
            search_id = int(search)

        usernames = []
        # Check for custom aliases
        with open('aliases', 'r') as f:
            for line in f:
                linesplit = line.split("=", 1)
                if message_split[1].lower() == linesplit[0]:
                    usernames = linesplit[1].rstrip().split(",")

        # If the command does not correspond to an alias, it's a list
        if usernames == []:
            usernames = list(set(message_split[1].lower().split(",")))

        # Retrieve the useful data
        if len(usernames) >= 20:
            usernames = usernames[:20]

        # Temporary message while working the request
        msg = '{0.author.mention}, currently retrieving data from MyAnimeList. Please wait !'.format(message)
        tmp = await client.send_message(message.channel, msg)

        users = []
        for username in usernames:
            user = User(username)
            if worktype == 'anime' or worktype == 'manga':
                if user.retrieveWorkList(worktype) == -1:
                    msg = '{0.author.mention}, one of the users does not seem to exist.'.format(message)
                    await client.edit_message(tmp, msg)
                    return
            else:
                msg = '{0.author.mention}, something went wrong.'.format(message)
                await client.edit_message(tmp, msg)
                return
            users.append(user)

        works = User.joinedWorksWithStats(users, worktype, id=search_id, title=search_title)
        usernames = [user.pseudo for user in users]
        print(works, flush=True)

        # Under this line, we no longer care about the type of search
        if len(works) == 1:
            work, stats = works.popitem()

            mal_url = "https://myanimelist.net/{}/{}".format(worktype, work.id)
            color = get_main_color(work.poster)

            result = discord.Embed(title=work.title, url=mal_url, color=color)
            result.set_footer(text=worktype.capitalize(), icon_url="https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png")
            result.set_thumbnail(url=work.poster)

            for pseudo in usernames:
                if pseudo.lower() in stats:
                    if stats[pseudo.lower()][1] == 1:
                        word = "Watching" if worktype == "anime" else "Reading"
                        if stats[pseudo.lower()][0] == 0:
                            result.add_field(name=pseudo, value="{} (Not yet rated)".format(word))
                        else:
                            result.add_field(name=pseudo, value="{} (Score : {})".format(word, stats[pseudo.lower()][0]))
                    elif stats[pseudo.lower()][1] == 2:
                        if stats[pseudo.lower()][0] == 0:
                            result.add_field(name=pseudo, value="Not yet rated")
                        else:
                            result.add_field(name=pseudo, value="Score : {}".format(stats[pseudo.lower()][0]))
                    elif stats[pseudo.lower()][1] == 3:
                        result.add_field(name=pseudo, value="On-hold")
                    elif stats[pseudo.lower()][1] == 4:
                        result.add_field(name=pseudo, value="Dropped")
                    elif stats[pseudo.lower()][1] == 6 and worktype == "anime":
                        result.add_field(name=pseudo, value="Plan to watch")
                    elif stats[pseudo.lower()][1] == 6 and worktype == "manga":
                        result.add_field(name=pseudo, value="Plan to read")
                    else:
                        result.add_field(name=pseudo, value="Unknown status")
                else:
                    result.add_field(name=pseudo, value="Not in list")


            msg = '{0.author.mention}, here are the results for your request : '.format(message)
            await client.edit_message(tmp, msg, embed=result)
        elif len(works) > 30:
            msg = '{0.author.mention}, your research provided too many results. Try to be more specific.'.format(message)
            await client.edit_message(tmp, msg)
        elif len(works) > 1:
            description = ""
            for work in works:
                description += work.title + "\n"
            description = "\n".join(sorted(description.split("\n")))
            result = discord.Embed(title="Conflicting titles", description=description, color=0xf7ed3b)

            msg = '{0.author.mention}, your research provided more than one result. Try to be more specific or use the exact title :'.format(message)
            await client.edit_message(tmp, msg, embed=result)
        else:
            msg = '{0.author.mention}, no such {1} was found for those users.'.format(message, worktype)
            await client.edit_message(tmp, msg)


def get_main_color(url):
    if os.path.isfile(url):
        img = Image.open(url)
    else:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

    colors = img.getcolors(72000)
    max_occurence, most_present = 0, 0
    try:
        for c in colors:
            if c[0] > max_occurence:
                (max_occurence, most_present) = c
        r, g, b = most_present
        return int('0x%02x%02x%02x' % (r, g, b), 16)
    except TypeError:
        raise Exception("Too many colors in the image")


# Let's start the bot
with open('app.settings', 'r') as f:
    for line in f:
        if line.startswith("token="):
            token = line.split("=", 1)[1]

if token != "":
    client.run(token.rstrip())
else:
    sys.exit("No token was provided.")
