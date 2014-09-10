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

from django.core.management.base import BaseCommand

import sys
import os

""" Update the database to change hardcoded audio sources.
* Collection root
* Location of mp3 (source) files in the docserver
* Location of derived files in the docserver
"""

import dashboard.models

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


class Command(BaseCommand):
    help = 'Run a module on a recording or a release'
    args = '<moduleid> <mbid>'

    def handle(self, *args, **options):
        if len(args) < 2:
            print "usage: %s <collmbid> <audiodir>"
            print "collmbid: The mbid of the collection to change"
            print "audiodir: the root of where the audio for this collection is"
            print "ensure that local_settings.AUDIO_ROOT is updated to the new derived location"
            print "Available collections:"
            for c in dashboard.models.Collection.objects.all():
                print c.id, c.name
            sys.exit()
        self.main(args[0], args[1])

    def main(self, collmbid, audiodir):
        try:
            c = dashboard.models.Collection.objects.get(pk=collmbid)
        except dashboard.models.Collection.DoesNotExist:
            print "Can't find this collection"
            return

        if os.path.exists(audiodir) and os.path.isdir(audiodir):
            if not audiodir.endswith("/"):
                audiodir += "/"
            c.root_directory = audiodir
            c.save()
        else:
            print "Argument %s is not a directory" % audiodir
            return

        print "done"
