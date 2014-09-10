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

from django import template

register = template.Library()

@register.simple_tag
def unprocessed_for_collection(moduleversion, collection):
    return moduleversion.unprocessed_files(collection)

@register.simple_tag
def processed_for_collection(moduleversion, collection):
    return moduleversion.processed_files(collection)

@register.simple_tag
def unprocessed_count_for_collection(moduleversion, collection):
    return len(unprocessed_for_collection(moduleversion, collection))

@register.simple_tag
def processed_count_for_collection(moduleversion, collection):
    return len(processed_for_collection(moduleversion, collection))
