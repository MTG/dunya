from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

import dashboard
import docserver
from docserver import jobs

class Command(BaseCommand):
    help = 'Run a module on a recording or a release'
    args = '<moduleid> <mbid>'
    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete data for this job first'),
        )

    def handle(self, *args, **options):
        if len(args) < 2:
            print "usage: <moduleid> <releasembid>|<recordingmbid> ..."
            print "if >1 id, they are taken to be recordings, otherwise it's tested for release first"
            print "modules:"
            for m in docserver.models.Module.objects.all():
                print " %s: %s/%s (v %s)" % (m.id, m.name, m.module, m.latest_version_number())
            raise CommandError("Not enough arguments")

        moduleid = int(args[0])
        mbid = args[1:]
        if len(mbid) > 1:
            recids = list(mbid)
        elif len(mbid) == 1:
            try:
                mbr = dashboard.models.MusicbrainzRelease.objects.get(mbid=mbid[0])
                files = dashboard.models.CollectionFile.objects.filter(directory__musicbrainzrelease=mbr)
                recids = [r.recordingid for r in files]
            except dashboard.models.MusicbrainzRelease.DoesNotExist:
                recids = [mbid[0]]

        if options["delete"]:
            module = docserver.models.Module.objects.get(pk=moduleid)
            version = module.get_latest_version()
            d = docserver.models.DerivedFile.objects.filter(
                    document__sourcefiles__file_type=module.source_type,
                    document__external_identifier__in=recids,
                    module_version=version)
            d.delete()

        jobs.run_module_on_recordings(moduleid, recids)
