from MALWork import Work

class Manga(Work):
    READING_STATUSES = {1: "Reading", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to read"}

    def __init__(self, manga_info_fromuserlist):
        # Initialize from a user's XML manga list
        id = manga_info_fromuserlist["series_mangadb_id"]
        title = manga_info_fromuserlist["series_title"]
        poster = manga_info_fromuserlist["series_image"]

        super().__init__(id = id, title = title, poster = poster)

    def __str__(self):
        return "Manga#{} : {}".format(self.id, self.title)
