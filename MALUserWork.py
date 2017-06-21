from MALWork import Work

class UserWork(Work):
    def __init__(self, work, score, status):
        self.work = work

        self.user_score = score
        self.user_status = status


    """ Test of equality between two UserWorks """
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        result = 17
        result += 31 * self.work.__hash__()
        result += 31 * hash(self.user_score)
        result += 31 * hash(self.user_status)

        return result
