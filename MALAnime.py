from MALWork import Work

class Anime(Work):
    WATCHING_STATUSES = {1: "Watching", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to watch"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        print("Anime#{id} : {title}", id = self.id, title = self.title)
