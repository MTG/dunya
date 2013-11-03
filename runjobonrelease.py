#!/usr/bin/env python

""" A test script to quicly run an algorithm on a release """

import sys

from dunya import settings
from django.core.management import setup_environ
setup_environ(settings)

from dashboard import models
from docserver import jobs

def main(module, mbid):
    files = models.CollectionFile.objects.filter(directory__musicbrainzrelease__mbid=mbid)
    recids = [r.recordingid for r in files]
    jobs.run_module_on_recordings(module, recids)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage: %s <moduleid> <releasembid>" % sys.argv[0]
        sys.exit()

    main(int(sys.argv[1]), sys.argv[2])
