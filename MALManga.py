from MALWork import Work

class Manga(Work):
    READING_STATUSES = {1: "Reading", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to read"}
    MANGA_TYPES = {0: "Unknown", 1: "Manga", 2: "Light Novel", 3: "One-shot", 5: "Manhwa"}

    def __init__(self, manga_info_fromuserlist):
        # Initialize from a user's XML manga list
        id = manga_info_fromuserlist["series_mangadb_id"]
        title = manga_info_fromuserlist["series_title"]
        poster = manga_info_fromuserlist["series_image"]
        type = int(manga_info_fromuserlist["series_type"])

        super().__init__(id = id, title = title, poster = poster, type = type)

    def __str__(self):
        return "Manga#{} : {}".format(self.id, self.title)

    def workType(self):
        return self.MANGA_TYPES[self.type]
