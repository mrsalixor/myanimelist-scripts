from MALWork import Work

class Anime(Work):
    WATCHING_STATUSES = {1: "Watching", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to watch"}

    def __init__(self, anime_info_fromuserlist):
        # Initialize from a user's XML anime list
        id = anime_info_fromuserlist["series_animedb_id"]
        title = anime_info_fromuserlist["series_title"]
        poster = anime_info_fromuserlist["series_image"]

        super().__init__(id = id, title = title, poster = poster)

    def __str__(self):
        return "Anime#{} : {}".format(self.id, self.title)
