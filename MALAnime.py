from MALWork import Work

class Anime(Work):
    WATCHING_STATUSES = {1: "Watching", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to watch"}
    ANIME_TYPES = {0: "Unknown", 1: "TV", 2: "OVA", 3: "Movie", 4: "Special", 5: "ONA", 6: "Music"}

    def __init__(self, anime_info_fromuserlist):
        id = int(anime_info_fromuserlist["series_animedb_id"])
        super().__init__(anime_info_fromuserlist, id = id)

        self._episodes = anime_info_fromuserlist["series_episodes"]


    def __str__(self):
        return "Anime#{} : {}".format(self.id, self.title)

    def workType(self):
        return self.ANIME_TYPES[self.type]


    """ Number of episodes of an anime """
    @property
    def episodes(self):
        return self._episodes

    @episodes.setter
    def episodes(self, episodes):
        self._episodes = episodes

    @episodes.deleter
    def episodes(self):
        del self._episodes
