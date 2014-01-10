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

from django.db.models.signals import post_syncdb

from docserver import models
from docserver import filetypes

import inspect

"""A post-syncdb hook to create DocumentConversion objects
"""
def create_docconverters(sender, **kwargs):
    for cl in inspect.getmembers(sender):
        if filetypes.FileType in cl.__bases__:
            inst = cl()

#post_syncdb.connect(create_docconverters)
