class Manga:
    READING_STATUSES = {1: "Reading", 2: "Completed", 3: "On-hold", 4: "Dropped", 6: "Plan to read"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        print("Manga#{id} : {title}", id = self.id, title = self.title)
