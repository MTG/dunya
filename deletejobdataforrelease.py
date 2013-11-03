#!/usr/bin/env python

""" Delete all the entries in the docserver for the files
    as part of this release for this job runner """

import sys

from dunya import settings
from django.core.management import setup_environ
setup_environ(settings)

from dashboard import models
from docserver import jobs
import docserver.models

def main(moduleid, mbid):
    files = models.CollectionFile.objects.filter(directory__musicbrainzrelease__mbid=mbid)
    recids = [r.recordingid for r in files]

    module = docserver.models.Module.objects.get(pk=moduleid)
    version = module.get_latest_version()

    docs = models.Document.objects.filter(
                sourcefiles__file_type=module.source_type,
                external_identifier__in=recids,

    derived = docserver.models.DerivedFile.objects.filter(
        derived_from__file_type=module.source_type,
        module_version=version,
        document__external_identifier__in=recids)
    count = derived.count()
    derived.delete()
    print "deleted %s items" % count

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage: %s <moduleid> <releasembid>" % sys.argv[0]
        sys.exit()

    main(int(sys.argv[1]), sys.argv[2])
