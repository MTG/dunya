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

import docserver.models

def rmtree(path):
    if os.path.exists(path):
        os.unlink(path)
    parts = path.split("/")
    path = "/" + os.path.join(*parts[:-1])
    while len(os.listdir(path)) == 0:
        os.rmdir(path)
        parts = path.split("/")
        path = "/" + os.path.join(*parts[:-1])

class Command(BaseCommand):
    help = 'Delete derivedfiles for all SourceFile entries with no associated file'

    def add_arguments(self, parser):
        parser.add_argument('-d',
            action='store_true',
            dest='delete',
            default=False,
            help='Actually delete items')


    def handle(self, *args, **options):
        delete = options["delete"]

        bad = []
        sourcefiles = docserver.models.SourceFile.objects.all()
        for i, s in enumerate(sourcefiles):
            if not os.path.exists(s.fullpath):
                print "%s/%s" % (i, len(sourcefiles)), s
                bad.append(s)
        if not delete:
            print "Run again with `-d` flag to delete all DerivedFiles associated with these SourceFiles"
        if delete:
            for b in bad:
                filetype = b.file_type
                modules = docserver.models.Module.objects.filter(source_type=filetype)
                document = b.document
                derived = document.derivedfiles.filter(module_version__module__in=modules)
                # TODO: This only deletes DerivedFiles directly related
                # to the source file, and does not chain through to others
                for d in derived:
                    for p in d.parts.all():
                        rmtree(p.fullpath)
                        p.delete()
                    d.delete()
                b.delete()
                if document.sourcefiles.count() == 0 and document.derivedfiles.count() == 0:
                    document.delete()

