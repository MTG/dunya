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

from django.db.models import Count
from carnatic.models import *
from social.models import *


def tag_cloud(modelid, modeltype):
    MAX_WEIGHT = 5

    tags = Annotation.objects.filter(entity_type=modeltype, entity_id=modelid).values('tag', 'entity_type').annotate(freq_tag=Count('tag'))
    for tag in tags:
        tag['content_type'] = modeltype

    if len(tags) > 0:
        # Calculate artist_tag, min and max counts.
        min_count = max_count = tags[0]['freq_tag']

        for tag in tags:
            tag['value'] = Tag.objects.get(pk=tag['tag']).name
            tag_count = tag['freq_tag']
            if tag_count < min_count:
                min_count = tag_count
            if max_count < tag_count:
                max_count = tag_count

        # Calculate count range. Avoid dividing by zero.
        rango = float(max_count - min_count)
        if rango == 0.0:
            rango = 1.0

        # Calculate artist_tag weights.
        for tag in tags:
            tag['freq_tag'] = int(
                MAX_WEIGHT * (tag['freq_tag'] - min_count) / rango)
    return tags
