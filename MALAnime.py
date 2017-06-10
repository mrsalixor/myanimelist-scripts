from MALWork import Work

class Anime(Work):
    WATCHING_STATUSES = {1: "Watching", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to watch"}
    ANIME_TYPES = {0: "Unknown", 1: "TV", 2: "OVA", 3: "Movie", 4: "Special", 5: "ONA", 6: "Music"}

    def __init__(self, anime_info_fromuserlist):
        # Initialize from a user's XML anime list
        id = anime_info_fromuserlist["series_animedb_id"]
        title = anime_info_fromuserlist["series_title"]
        poster = anime_info_fromuserlist["series_image"]
        type = int(anime_info_fromuserlist["series_type"])

        super().__init__(id = id, title = title, poster = poster, type = type)

    def __str__(self):
        return "Anime#{} : {}".format(self.id, self.title)

    def workType(self):
        return self.ANIME_TYPES[self.type]
