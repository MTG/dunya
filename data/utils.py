# -*- coding: UTF-8 -*-

# Copyright 2013-2018 Music Technology Group - Universitat Pompeu Fabra
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


def get_user_permissions(user):
    """Get the collection permissions that a user is able to access.
    Collection permissions are defined in data.Collection.permission"""

    permission = ["U"]
    if user.is_staff:
        permission = ["S", "R", "U"]
    elif user.has_perm('data.access_restricted'):
        permission = ["R", "U"]
    return permission
