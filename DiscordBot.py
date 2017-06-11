import discord
import asyncio

import csv
import urllib.request
import codecs

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as', flush=True)
    print(client.user.name, flush=True)
    print(client.user.id, flush=True)
    print('------', flush=True)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('!anime_stats') or message.content.lower().startswith('!manga_stats'):
        if message.content.lower().startswith('!anime_stats'):
            worktype = 'anime'
        elif message.content.lower().startswith('!manga_stats'):
            worktype = 'manga'
        else:
            return

        message_split = message.content.split(" ", 1)

        if len(message_split) <= 1:
            await client.send_message(message.channel, 'Please type `!{}_stats <id>`.'.format(worktype))
        else:
            search = message_split[1].strip()
            search_id = 0
            search_title = ""

            if not search.isnumeric():
                search_title = search
            else:
                search_id = int(search)

            # Retrieval of the .csv file
            url = 'http://cocchi.iiens.net/MALUpdater/shared_works_' + worktype + '.csv'
            req = urllib.request.urlopen(url)
            csvfile = csv.reader(codecs.iterdecode(req, 'utf-8'), delimiter='|')

            lines_match = []

            # Let's find the anime that has the id or title provided in the query
            for index, line in enumerate(csvfile):
                if index == 0:
                    pseudos = [pseudo for pseudo in line]
                else:
                    id = int(line[0])
                    title = line[1]

                    if id == search_id or (search_title != "" and title.lower().startswith(search_title.lower())):
                        lines_match.append(line)

            # Under this line, we no longer care about the type of search
            print(lines_match, flush=True)
            if len(lines_match) == 1:
                id = lines_match[0][0]
                title = lines_match[0][1]
                poster_url = lines_match[0][3]
                mal_url = "https://myanimelist.net/{}/{}".format(worktype, id)

                result = discord.Embed(title=title, url=mal_url, color=0xf7ed3b)
                result.set_footer(text=worktype.capitalize(), icon_url="https://myanimelist.cdn-dena.com/img/sp/icon/apple-touch-icon-256.png")
                result.set_thumbnail(url=poster_url)

                statuses_scores = [s for s in lines_match[0][4:4+len(pseudos)]]

                for index, pseudo in enumerate(pseudos):
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

                await client.send_message(message.channel, embed=result)
            elif len(lines_match) > 1:
                await client.send_message(message.channel, 'Your research provided more than one result. Try once again with the exact title :')

                description = ""
                for line in lines_match:
                    description += line[1] + "\n"
                result = discord.Embed(title="Conflicting titles", description=description, color=0xf7ed3b)

                await client.send_message(message.channel, embed=result)
            else:
                await client.send_message(message.channel, 'No such {} was found.'.format(worktype))


client.run('MzIzMjExNTQzNzQxNDY0NTc4.DB34RA.bdVDgEe9KXHKiBhwoRoYtojfHGY')
