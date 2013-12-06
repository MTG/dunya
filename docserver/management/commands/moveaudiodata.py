from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option

import sys
import os

""" Update the database to change hardcoded audio sources.
* Collection root
* Location of mp3 (source) files in the docserver
* Location of derived files in the docserver
"""

import dashboard.models
import docserver.models

from django.conf import settings

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


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
        derivedlocation = settings.AUDIO_ROOT

        try:
            c = dashboard.models.Collection.objects.get(pk=collmbid)
        except dashboard.models.Collection.DoesNotExist:
            print "Can't find this collection"
            return

        if os.path.exists(audiodir) and os.path.isdir(audiodir):
            oldroot = c.root_directory
            if not audiodir.endswith("/"):
                audiodir += "/"
            c.root_directory = audiodir
            c.save()

            sourcefiles = docserver.models.SourceFile.objects.all()
            print "Updating source files"
            with transaction.atomic():
                for s in sourcefiles:
                    oldpath = s.path
                    newpath = oldpath.replace(oldroot, audiodir)
                    s.path = newpath
                    s.save()
        else:
            print "Argument %s is not a directory" % audiodir
            return

        print "done"
