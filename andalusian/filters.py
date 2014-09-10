# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

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
        ob = {"name": self.name, "type": self.type}
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


class Generation(SearchFilter):
    name = "generation"
    type = "rangeslider"
    step = 10
    datalist = [1850, 2020]


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


class WorkDate(SearchFilter):
    name = "date"
    type = "rangelist"
    datalist = [1700, 1800, 1850, 1900, 1930, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]


class Text(SearchFilter):
    name = "name"
    type = "text"
