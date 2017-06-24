class Work:
    def __init__(self, infos, **kwargs):
        self._title = infos["series_title"]
        self._alt_titles = infos["series_synonyms"]
        self._type = int(infos["series_type"])
        self._status = int(infos["series_status"])
        self._series_start = infos["series_start"]
        self._series_end = infos["series_end"]
        self._poster = infos["series_image"]

        self._id = kwargs.get("id")


    """ Test of equality between two Works """
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        result = 17
        result += 31 * hash(self._id)
        result += 31 * hash(self._title)
        result += 31 * hash(self._alt_titles)
        result += 31 * hash(self._type)
        result += 31 * hash(self._status)
        result += 31 * hash(self._series_start)
        result += 31 * hash(self._series_end)
        result += 31 * hash(self._poster)
        return result


    """ Return the type of work (ONA, Movie, LN ...) in a readable format """
    def workType(self):
        return ""

    """ Getter : full raw data for a work """
    @property
    def data(self):
        return self._data

    """ Getter : genres of a work """
    @property
    def genres(self):
        try:
            genres_with_id = [(int(genre_with_id.split("/")[0]), genre_name)
                              if genre_with_id is not None and genre_name is not None
                              else (0, '')
                              for genre_with_id, genre_name in self._data["genres"]]
        except ValueError:
            genres_with_id = [(int(self._data["genres"][0].split("/")[0]), self._data["genres"][1])]
        except TypeError:
            genres_with_id = [(0, 'Unknown')]

        return genres_with_id


    """ Work id """
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @id.deleter
    def id(self):
        del self._id


    """ Work title """
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @title.deleter
    def title(self):
        del self._title


    """ Work alternative titles """
    @property
    def alt_titles(self):
        return self._alt_titles

    @alt_titles.setter
    def alt_titles(self, alt_titles):
        self._alt_titles = alt_titles

    @alt_titles.deleter
    def alt_titles(self):
        del self._alt_titles


    """ Work type """
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @type.deleter
    def type(self):
        del self._type


    """ Work status """
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @status.deleter
    def status(self):
        del self._status


    """ Work start date of publication / airing """
    @property
    def series_start(self):
        return self._series_start

    @series_start.setter
    def series_start(self, series_start):
        self._series_start = series_start

    @series_start.deleter
    def series_start(self):
        del self._series_start


    """ Work end date of publication / airing """
    @property
    def series_end(self):
        return self._series_end

    @series_end.setter
    def series_end(self, series_end):
        self._series_end = series_end

    @series_end.deleter
    def series_start(self):
        del self._series_end


    """ Work poster """
    @property
    def poster(self):
        return self._poster

    @poster.setter
    def poster(self, poster):
        self._poster = poster

    @poster.deleter
    def poster(self):
        del self._poster
