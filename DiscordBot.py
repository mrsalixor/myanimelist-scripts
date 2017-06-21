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

    if message.content.lower().startswith('!help'):
        msg = "```!anime_stats <user1,...,userN> <id/title> : scores and statuses of users for a given anime\n"
        msg += "!manga_stats <user1,...,userN> <id/title> : scores and statuses of users for a given manga```"
        await client.send_message(message.channel, msg)

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
                if user.retrieveWorkList(worktype) < 0:
                    msg = '{0.author.mention}, one of the users does not seem to exist.'.format(message)
                    await client.edit_message(tmp, msg)
                    return
            else:
                msg = '{0.author.mention}, something went wrong.'.format(message)
                await client.edit_message(tmp, msg)
                return
            users.append(user)

        path = "csvfiles"
        if not os.path.isdir(path):
            os.makedirs(path)
        filename = '_'.join(usernames+[worktype]) + ".csv"
        filename = os.path.join(path, filename)

        # Create the CSV file if it hasn't been updated in an hour
        if not os.path.isfile(filename):
            User.toCSV(users, destination=filename, worktype=worktype)
        else:
            if time.time() - os.stat(filename)[stat.ST_MTIME] > 3600:
                User.toCSV(users, destination=filename, worktype=worktype)

        lines_match = []
        # Retrieval of the .csv file
        with open(filename, 'r', encoding='utf-8') as f:
            csvfile = csv.reader(f, delimiter='|')

            # Let's find the anime that has the id or title provided in the query
            for index, line in enumerate(csvfile):
                if index == 0:
                    usernames = line
                elif index == 1:
                    continue
                else:
                    id = int(line[0])
                    title = line[1]

                    if id == search_id or title.lower() == search_title.lower():
                        lines_match = [line]
                        break
                    elif search_title != "" and title.lower().startswith(search_title.lower()):
                        lines_match.append(line)

        # Under this line, we no longer care about the type of search
        if len(lines_match) == 1:
            id = lines_match[0][0]
            title = lines_match[0][1]
            poster_url = lines_match[0][3]
            mal_url = "https://myanimelist.net/{}/{}".format(worktype, id)
            color = get_main_color(poster_url)

            result = discord.Embed(title=title, url=mal_url, color=color)
            result.set_footer(text=worktype.capitalize(), icon_url="https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png")
            result.set_thumbnail(url=poster_url)

            statuses_scores = [s for s in lines_match[0][4:4+len(usernames)]]

            for index, pseudo in enumerate(usernames):
                if statuses_scores[index] == 'O':
                    result.add_field(name=pseudo, value="On-hold")
                elif statuses_scores[index] == 'D':
                    result.add_field(name=pseudo, value="Dropped")
                elif statuses_scores[index] == 'P' and worktype == "anime":
                    result.add_field(name=pseudo, value="Plan to watch")
                elif statuses_scores[index] == 'P' and worktype == "manga":
                    result.add_field(name=pseudo, value="Plan to read")
                elif statuses_scores[index].isnumeric():
                    if int(statuses_scores[index]) == 0:
                        result.add_field(name=pseudo, value="Not yet rated")
                    else:
                        result.add_field(name=pseudo, value="Score : " + statuses_scores[index])
                else:
                    result.add_field(name=pseudo, value="Not in list")

            msg = '{0.author.mention}, here are the results for your request : '.format(message)
            await client.edit_message(tmp, msg, embed=result)
        elif len(lines_match) > 1:
            description = ""
            for line in lines_match:
                description += line[1] + "\n"
            result = discord.Embed(title="Conflicting titles", description=description, color=0xf7ed3b)

            msg = '{0.author.mention}, your research provided more than one result. Try once again with the exact title :'.format(message)
            await client.edit_message(tmp, msg, embed=result)
        else:
            msg = '{0.author.mention}, no such {1} was found for those users.'.format(message, worktype)
            await client.edit_message(tmp, msg)


def get_main_color(url):
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
