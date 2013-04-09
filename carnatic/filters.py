import models

"""
Query criteria and values for filtering objects

Classes should inherit from SearchFilter and need at least name and type.
datasource must be implemented as a property so that it lazily
evaluates and doesn't cause an importerror.
"""

class SearchFilter(object):
    @property
    def object(self):
        ob = {"name": self.name,
                "type": self.type
             }
        if hasattr(self, "datasource"):
            ob["data"] = [o.name for o in self.datasource.objects.all()]
        elif hasattr(self, "datalist"):
            ob["data"] = self.datalist
        if hasattr(self, "multiselect"):
            ob["multiselect"] = self.multiselect
        if hasattr(self, "step"):
            ob["step"] = self.step
        return ob

class School(SearchFilter):
    name = "school"
    multiselect = True
    type = "list"
    @property
    def datasource(self):
        return models.MusicalSchool

class Region(SearchFilter):
    name = "region"
    multiselect = True
    type = "list"
    @property
    def datasource(self):
        return models.GeographicRegion

class Generation(SearchFilter):
    name = "generation"
    type = "rangeslider"
    step = 10
    datalist = [1850, 2020]

class Venue(SearchFilter):
    name = "venue"
    type = "list"
    multiselect = True
    @property
    def datasource(self):
        return models.Sabbah

class Instrument(SearchFilter):
    name = "instrument"
    type = "list"
    multiselect = True
    @property
    def datasource(self):
        return models.Instrument

class Form(SearchFilter):
    name = "form"
    type = "list"
    multiselect = True
    @property
    def datasource(self):
        return models.Form

class Language(SearchFilter):
    name = "language"
    type = "list"
    multiselect = True
    @property
    def datasource(self):
        return models.Language

class WorkDate(SearchFilter):
    name = "date"
    type = "rangelist"
    datalist = [1700, 1800, 1850, 1900, 1930, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

class Text(SearchFilter):
    name = "name"
    type = "text"
