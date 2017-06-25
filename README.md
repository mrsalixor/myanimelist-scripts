# myanimelist-scripts
This project is mainly aimed at experimenting with both MyAnimeList's API and Discord's API.

## Classes

Two main classes are defined in this project :
* `MALWork` which represents either an Anime or a Manga
* `MALUser` which represents a MyAnimeList user and a list of works they added to their list

The classes `MALAnime` and `MALManga` inherits from `MALWork` and serve to specialize its functions and attributes depending on the type of work.

## Discord bot

A Discord bot is also found at `DiscordBot.py`. It will provide with a simple bot that you can add to your servers.

### Setup


In order to run the bot, you'll have to provide an `app.settings` file with the token provided by Discord for this bot :

```
token=<token>
```

You can also add aliases for user lists in an `aliases` file as such. When typing commands to the bot, you will be able to use those aliases instead of manually type the lists once again :

```
alias1=user1,...,userN
alias2=user1,...,userM
...
aliasK=user1,...,userZ
```

### Utility

There are two main functionalities provided by this bot :
* `!anime_stats <user1,...,userN> <id/title>` : shows the list of scores or watching status for those users
* `!manga_stats <user1,...,userN> <id/title>` : shows the list of scores or reading status for those users
- `!anime_favgenre <user>` : the bot will show the favorite anime genres of a user
- `!manga_favgenre <user>` : the bot will show the favorite manga genres of a user

_Be aware that in order to use the `!anime_favgenre` or `!manga_favgenre` commands, a heavy caching of anime and manga data through [Jikan's API](https://jikan.me/) has to be made before running the bot. You can use the functions provided in `Scrapper.py` in order to cache the data._
