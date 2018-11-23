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
import uuid

from rest_framework.exceptions import ValidationError


def get_collection_ids_from_request_or_error(request):
    """Read the `Dunya-Collection` header from a request and return the values.
    This header consists of one or more UUIDs, separated by a comma.

    Returns:
        A list of UUIDs present in the header
    Raises:
        Django Rest Framework ValidationError (HTTP 400) if any of the items in the list are not a UUID"""

    header = request.META.get('HTTP_DUNYA_COLLECTION', None)
    collection_ids = []
    if header:
        parts = header.replace(' ', '').split(',')
        for p in parts:
            try:
                uuid.UUID(p)
                collection_ids.append(p)
            except ValueError:
                raise ValidationError('Dunya-Collection header is not a UUID or list of UUID')
    return collection_ids
