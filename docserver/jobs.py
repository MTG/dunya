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

from __future__ import absolute_import
from django.db import transaction

import importlib
import os
import json
import logging
import time

from docserver import models
import dashboard
import numpy as np

from django.conf import settings
from dunya.celery import app

class DatabaseLogHandler(logging.Handler):
    def handle(self, record):
        documentid = getattr(record, "documentid", None)
        sourcefileid = getattr(record, "sourcefileid", None)
        modulename = getattr(record, "modulename", None)
        moduleversion = getattr(record, "moduleversion")

        modv = None
        if modulename and moduleversion:
            try:
                mod = models.Module.objects.get(module=modulename)
                modv = mod.versions.get(version=moduleversion)
            except (models.Module.DoesNotExist, models.ModuleVersion.DoesNotExist):
                pass

        sourcef = None
        if sourcefileid:
            try:
                sourcef = models.SourceFile.objects.get(pk=int(sourcefileid))
            except models.SourceFile.DoesNotExist:
                pass
        doc = None
        if documentid:
            try:
                doc = models.Document.objects.get(pk=int(documentid))
                models.DocumentLogMessage.objects.create(document=doc, moduleversion=modv, sourcefile=sourcef, level=record.levelname, message=record.getMessage())
            except models.Document.DoesNotExist:
                print "no document, can't create a log file"
        else:
            print "no document, can't create a log file"

logger = logging.getLogger("extractor")
logger.setLevel(logging.DEBUG)
logger.addHandler(DatabaseLogHandler())

def _get_module_instance_by_path(modulepath):
    args = {}
    try:
        redis_host = settings.WORKER_REDIS_HOST
        args = {"redis_host": redis_host}
    except AttributeError:
        pass
    mod, clsname = modulepath.rsplit(".", 1)
    package = importlib.import_module(mod)
    cls = getattr(package, clsname)
    return cls(**args)

def create_module(modulepath, collections):
    instance = _get_module_instance_by_path(modulepath)
    try:
        sourcetype = models.SourceFileType.objects.get(extension=instance.__sourcetype__)
    except models.SourceFileType.DoesNotExist as e:
        raise Exception("Cannot find source file type '%s'" % instance.__sourcetype__, e)

    module = models.Module.objects.create(name=modulepath.rsplit(".", 1)[1],
                    slug=instance.__slug__,
                    depends=instance.__depends__,
                    module=modulepath,
                    source_type=sourcetype)
    module.collections.add(*collections)
    get_latest_module_version(module.pk)

def get_latest_module_version(themod_id=None):
    if themod_id:
        modules = [models.Module.objects.get(pk=themod_id)]
    else:
        modules = models.Module.objects.all()
    for m in modules:
        instance = _get_module_instance_by_path(m.module)
        version = instance.__version__
        v = "%s" % version

        versions = m.versions.filter(version=version)
        if not len(versions):
            models.ModuleVersion.objects.create(module=m, version=v)

@app.task
def delete_moduleversion(vid):
    version = models.ModuleVersion.objects.get(pk=vid)
    print "deleting moduleversion", version
    files = version.derivedfile_set.all()
    for f in files:
        for p in f.parts():
            path = p.path
            os.unlink(path)
        f.delete()
    version.delete()
    print "done"

class NumPyArangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist() # or map(int, obj)
        return json.JSONEncoder.default(self, obj)

def _save_file(collection, recordingid, version, slug, partslug, partnumber, extension, data):
    recordingstub = recordingid[:2]
    reldir = os.path.join(collection, recordingstub, recordingid, slug, version)
    fdir = os.path.join(settings.AUDIO_ROOT, reldir)
    try:
        os.makedirs(fdir)
    except OSError:
        pass
    fname = "%s-%s-%s.%s" % (slug, partslug, partnumber, extension)

    fullname = os.path.join(fdir, fname)
    fullrelname = os.path.join(reldir, fname)
    fp = open(fullname, "wb")
    if extension == "json":
        data = json.dumps(data, fp, cls=NumPyArangeEncoder)

    if not isinstance(data, basestring):
        print "Data is not a string-ish thing. instead it's %s" % type(data)
    fp.write(data)
    fp.close()
    return fullname, fullrelname, len(data)

@app.task
def process_document(documentid, moduleversionid):
    version = models.ModuleVersion.objects.get(pk=moduleversionid)
    module = version.module
    instance = _get_module_instance_by_path(module.module)

    document = models.Document.objects.get(pk=documentid)

    sfiles = document.sourcefiles.filter(file_type=module.source_type)
    if len(sfiles):
        # TODO: If there is more than 1 source file
        s = sfiles[0]
        fname = s.fullpath.encode("utf-8")
        starttime = time.time()
        results = instance.process_document(document.pk, s.pk, document.external_identifier, fname)
        endtime = time.time()
        total_time = int(endtime-starttime)

        collectionid = document.collection.collectionid
        moduleslug = module.slug
        with transaction.atomic():
            for dataslug, contents in results.items():
                print "data", dataslug
                print "type", type(contents)
                outputdata = instance.__output__[dataslug]
                extension = outputdata["extension"]
                mimetype = outputdata["mimetype"]
                multipart = outputdata.get("parts", False)
                print "multiparts", multipart
                df = models.DerivedFile.objects.create(document=document, derived_from=s,
                        module_version=version, outputname=dataslug, extension=extension,
                        mimetype=mimetype, computation_time=total_time)

                if not multipart:
                    contents = [contents]
                for i, partdata in enumerate(contents, 1):
                    saved_name, rel_path, saved_size = _save_file(collectionid, document.external_identifier,
                            version.version, moduleslug, dataslug, i, extension, partdata)
                    df.save_part(i, rel_path, saved_size)

def run_module(moduleid):
    module = models.Module.objects.get(pk=moduleid)
    collections = module.collections.all()
    for c in collections:
        run_module_on_collection(c.pk, module.pk)

def run_module_on_recordings(moduleid, recids):
    module = models.Module.objects.get(pk=moduleid)
    version = module.get_latest_version()
    print "running module %s on %s files" % (module, len(recids))
    if version:
        print "version", version, version.pk
        # All documents that don't already have a derived file for this module version
        docs = models.Document.objects.filter(
                sourcefiles__file_type=module.source_type,
                external_identifier__in=recids,
                ).exclude(derivedfiles__module_version=version)
        for d in docs:
            print "  document", d
            print "  docid", d.pk
            process_document.delay(d.pk, version.pk)

def run_module_on_collection(collectionid, moduleid):
    collection = models.Collection.objects.get(pk=collectionid)
    module = models.Module.objects.get(pk=moduleid)
    version = module.get_latest_version()
    print "running module", module, "on collection", collection
    if version:
        print "version", version
        # All documents that don't already have a derived file for this module version
        docs = models.Document.objects.filter(sourcefiles__file_type=module.source_type,
                collection=collection).exclude(derivedfiles__module_version=version)
        for i, d in enumerate(docs, 1):
            print "  document %s/%s - %s" % (i, len(docs), d)
            process_document.delay(d.pk, version.pk)
