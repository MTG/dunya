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

from __future__ import print_function

import os

from django.core.management.base import BaseCommand

import docserver.models


def rmderived(d):
    """Remove all file parts from a derived file, and then
       remove the common directory tree in one step"""
    paths = []
    for p in range(1, d.num_parts + 1):
        paths.append(d.full_path_for_part(p))
    if not paths:
        return
    for pth in paths:
        if os.path.exists(pth):
            os.unlink(pth)
    # Check if all derived parts appear in the same directory (they should)
    dirs = []
    for pth in paths:
        parts = pth.split("/")
        pth = "/" + os.path.join(*parts[:-1])
        dirs.append(pth)
    if os.path.commonprefix(dirs) == dirs[0]:
        rmtree(dirs[0])
    else:
        for d in dirs:
            rmtree(d)


def rmtree(path):
    # Delete file
    if os.path.exists(path):
        os.unlink(path)

    # Path of containing directory
    parts = path.split("/")
    path = "/" + os.path.join(*parts[:-1])
    if os.path.exists(path):
        exists = True
        numfiles = len(os.listdir(path))
    else:
        exists = False
        numfiles = 0
    while not exists or numfiles == 0:
        # Keep moving up the directory tree if the dir is empty
        # or it does not exist
        if exists:
            os.rmdir(path)
        parts = path.split("/")
        path = "/" + os.path.join(*parts[:-1])
        if os.path.exists(path):
            exists = True
            numfiles = len(os.listdir(path))
        else:
            exists = False
            numfiles = 0


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
                print("%s/%s %s" % (i, len(sourcefiles), s))
                bad.append(s)
        print("got %s item%s to remove" % (len(bad), "" if len(bad) == 1 else "s"))
        if not delete:
            print("Run again with `-d` flag to delete all DerivedFiles associated with these SourceFiles")
        if delete:
            print("removing...")
            for b in bad:
                filetype = b.file_type
                modules = docserver.models.Module.objects.filter(source_type=filetype)
                document = b.document
                derived = document.derivedfiles.filter(module_version__module__in=modules)
                # TODO: This only deletes DerivedFiles directly related
                # to the source file, and does not chain through to others
                for d in derived:
                    rmderived(d)
                    d.delete()
                b.delete()
                if document.sourcefiles.count() == 0 and document.derivedfiles.count() == 0:
                    document.delete()
