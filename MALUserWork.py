from MALWork import Work

class UserWork(Work):
    def __init__(self, work, score, status):
        self.work = work

        self.user_score = score
        self.user_status = status

    def __hash__(self):
        result = 17
        result += 31 * int(self.work.id)
        result += 31 * hash(self.work.title)
        result += 31 * hash(self.work.poster)
        return result
