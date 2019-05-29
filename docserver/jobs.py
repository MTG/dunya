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

import importlib
import json
import logging
import os
import time

import django.utils.timezone
import numpy as np
import six
from django.conf import settings
from django.db import transaction

from dashboard.log import logger
from docserver import log
from docserver import models
from dunya.celery import app


class DatabaseLogHandler(logging.Handler):
    def handle(self, record):
        documentid = getattr(record, "documentid", None)
        sourcefileid = getattr(record, "sourcefileid", None)
        modulename = getattr(record, "modulename", None)
        moduleversion = getattr(record, "moduleversion", None)

        modv = None
        if modulename and moduleversion:
            try:
                mod = models.Module.objects.get(slug=modulename)
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
                models.DocumentLogMessage.objects.create(document=doc, moduleversion=modv, sourcefile=sourcef,
                                                         level=record.levelname, message=record.getMessage())
            except models.Document.DoesNotExist:
                logger.error("no document, can't create a log file")
        else:
            logger.error("no document, can't create a log file")


extractor_logger = logging.getLogger("extractor")
extractor_logger.setLevel(logging.DEBUG)
extractor_logger.addHandler(DatabaseLogHandler())


def _get_module_instance_by_path(modulepath):
    args = {}
    try:
        redis_host = settings.WORKER_REDIS_HOST
        args = {"redis_host": redis_host}
    except AttributeError:
        pass
    # try:
    mod, clsname = modulepath.rsplit(".", 1)
    package = importlib.import_module(mod)
    cls = getattr(package, clsname)
    return cls(**args)
    # except ImportError:
    #    return None


def create_module(modulepath, collections):
    instance = _get_module_instance_by_path(modulepath)
    try:
        sourcetype = models.SourceFileType.objects.get_by_slug(instance._sourcetype)
    except models.SourceFileType.DoesNotExist as e:
        raise Exception("Cannot find source file type '%s'" % instance._sourcetype, e)
    if models.Module.objects.filter(slug=instance._slug).exists():
        raise Exception("A module with this slug (%s) already exists" % instance._slug)

    module = models.Module.objects.create(
        name=modulepath.rsplit(".", 1)[1],
        slug=instance._slug,
        depends=instance._depends,
        many_files=instance._many_files,
        module=modulepath,
        source_type=sourcetype)
    module.collections.add(*collections)
    get_latest_module_version(module.pk)
    return module


def get_latest_module_version(themod_id=None):
    """ Create a new ModuleVersion if this module has been
        updated.
        If no argument is given, update all modules. """
    if themod_id:
        modules = models.Module.objects.filter(pk=themod_id)
    else:
        modules = models.Module.objects.filter(disabled=False)
    for m in modules:
        logger.info("module %s" % m)
        instance = _get_module_instance_by_path(m.module)
        logger.info("instance %s" % instance)
        if instance:
            if m.disabled:  # if we were disabled and exist again, reenable.
                m.disabled = False
                m.save()
            version = instance._version
            v = "%s" % version

            versions = m.versions.filter(version=version)
            if not len(versions):
                models.ModuleVersion.objects.create(module=m, version=v)
        else:
            m.disabled = True
            m.save()


@app.task
def delete_moduleversion(vid):
    version = models.ModuleVersion.objects.get(pk=vid)
    logger.info("deleting moduleversion %s" % version)
    files = version.derivedfile_set.all()
    for f in files:
        for pn in range(1, f.num_parts + 1):
            path = f.full_path_for_part(pn)
            try:
                os.unlink(path)
                dirname = os.path.dirname(path)
                if len(os.listdir(dirname)) == 0:
                    # If this directory is empty, remove it and all empty
                    # parent dirs. May throw OSError (not really an error)
                    os.removedirs(dirname)
            except OSError:
                pass  # if the file doesn't exist, not really an error
        f.delete()
    module = version.module
    version.delete()
    logger.info("done")


@app.task
def delete_module(mid):
    module = models.Module.objects.get(pk=mid)
    logger.info("deleting entire module %s" % module)
    for v in module.versions.all():
        delete_moduleversion(v.pk)
    logger.info("done")


@app.task
def delete_collection(cid):
    """ Delete a collection and all its documents from the docserver.
    Also remove the physical files from all the derivedfiles that
    have been created for the documents.
    """
    collection = models.Collection.objects.get(pk=cid)

    collections = []
    for d in collection.document.all():
        if len(d.collections) > 1:
            d.collections.remove(collection)
        else:
            collections.add(d)

    dfs = models.DerivedFile.objects.filter(document__collections__in=collections)
    paths = []
    for df in dfs:
        for pn in range(1, df.num_parts + 1):
            path = df.full_path_for_part(pn)
            paths.append(path)
    for f in paths:
        os.remove(f)
    collection.delete()


class NumPyArangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # or map(int, obj)
        return json.JSONEncoder.default(self, obj)


def _save_file(derivedfile, partnumber, extension, data):
    fdir = derivedfile.directory()
    try:
        os.makedirs(fdir)
    except OSError:
        logger.warn("Error making directory %s" % fdir)
        pass

    fname = derivedfile.filename_for_part(partnumber)

    fullname = os.path.join(fdir, fname)
    try:
        # json module requires a string file-pointer. Other data could be either a string
        # or bytes. Convert all strings to bytes and write
        if extension == "json":
            with open(fullname, "w") as fp:
                json.dump(data, fp, cls=NumPyArangeEncoder)
        else:
            if isinstance(data, six.string_types):
                data = data.encode("utf-8")
            with open(fullname, "wb") as fp:
                fp.write(data)
        fp.close()
    except OSError:
        logger.warn("Error writing to file %s" % fullname)
        logger.warn("Probably a permissions error")


def _get_worker_from_hostname(hostname):
    if hostname and "@" in hostname:
        hostname = hostname.split("@")[1]
    try:
        worker = models.Worker.objects.get(hostname=hostname)
    except models.Worker.DoesNotExist:
        # Not the end of the world, though we really should have a
        # Worker object for all our hosts
        worker = None
    return worker


def _save_process_results(version, instance, document, worker, results, starttime, endtime):
    total_time = int(endtime - starttime)

    module = version.module
    with transaction.atomic():
        for dataslug, contents in results.items():
            outputdata = instance._output[dataslug]
            extension = outputdata["extension"]
            mimetype = outputdata["mimetype"]
            multipart = outputdata.get("parts", False)
            logger.info("data %s (%s)" % (dataslug, type(contents)))
            logger.info("multiparts %s" % multipart)

            if not multipart:
                contents = [contents]
            df, created = models.DerivedFile.objects.get_or_create(
                document=document,
                module_version=version, outputname=dataslug, extension=extension,
                mimetype=mimetype, defaults={'computation_time': total_time, 'num_parts': len(contents)})
            if not created:
                df.date = django.utils.timezone.now()
                df.num_parts = len(contents)
                df.save()
            if worker:
                df.essentia = worker.essentia
                df.pycompmusic = worker.pycompmusic
                df.save()

            for i, partdata in enumerate(contents, 1):
                _save_file(df, i, extension, partdata)

    # When we've finished, log that we processed the file. If this throws an
    # exception, we won't do the log.
    log.log_processed_file(instance.hostname, document.external_identifier, version.pk)


@app.task
def process_collection(collectionid, moduleversionid):
    version = models.ModuleVersion.objects.get(pk=moduleversionid)
    module = version.module
    instance = _get_module_instance_by_path(module.module)

    hostname = process_collection.request.hostname
    worker = _get_worker_from_hostname(hostname)

    instance.hostname = hostname

    # if the extractor run over all the collection then the document
    # has the same id of the collection and the result is
    # set to this document
    collection = models.Collection.objects.get(pk=collectionid)
    sfiles = models.SourceFile.objects.filter(document__collections=collection, file_type=module.source_type)

    document, created = models.Document.objects.get_or_create(
        title=collection.name,
        external_identifier=collection.collectionid)
    if created:
        document.collections.add(collection)

    if len(sfiles):
        id_fnames = [(s.document.external_identifier, s.fullpath.encode("utf8")) for s in sfiles]
        starttime = time.time()
        results = instance.process_collection(document.pk, id_fnames)
        endtime = time.time()

        if results:
            _save_process_results(version, instance, document, worker, results, starttime, endtime)


@app.task
def process_document(documentid, moduleversionid):
    version = models.ModuleVersion.objects.get(pk=moduleversionid)
    module = version.module
    instance = _get_module_instance_by_path(module.module)

    hostname = process_document.request.hostname
    worker = _get_worker_from_hostname(hostname)
    instance.hostname = hostname

    document = models.Document.objects.get(pk=documentid)
    sfiles = document.sourcefiles.filter(file_type=module.source_type)
    if len(sfiles):
        s = sfiles[0]
        starttime = time.time()
        results = instance.process_document(document.pk, s.pk, document.external_identifier, s.fullpath)
        endtime = time.time()

        if results:
            _save_process_results(version, instance, document, worker, results, starttime, endtime)


def run_module(moduleid, versionid=None):
    module = models.Module.objects.get(pk=moduleid)
    collections = module.collections.all()
    for c in collections:
        run_module_on_collection(c.pk, module.pk, versionid)


def run_module_on_recordings(moduleid, recids):
    module = models.Module.objects.get(pk=moduleid)
    version = module.get_latest_version()
    logger.info("running module %s on %s files" % (module, len(recids)))
    if version:
        logger.info("version %s %s" % (version, version.pk))
        # All documents that don't already have a derived file for this module version
        docs = models.Document.objects.filter(
            sourcefiles__file_type=module.source_type,
            external_identifier__in=recids,
        ).exclude(derivedfiles__module_version=version)
        for d in docs:
            logger.info("  document %s" % d)
            logger.info("  docid %s" % d.pk)
            process_document.delay(d.pk, version.pk)


@app.task
def run_module_on_collection(collectionid, moduleid, versionid=None):
    collection = models.Collection.objects.get(pk=collectionid)
    module = models.Module.objects.get(pk=moduleid)
    if versionid:
        version = module.versions.get(pk=versionid)
    else:
        version = module.get_latest_version()
    logger.info("running module %s on collection %s" % (module, collection))
    if version:
        logger.info("version %s" % version)

        if module.many_files:
            process_collection.delay(collection.pk, version.pk)
        else:
            # All documents that don't already have a derived file for this module version
            docs = models.Document.objects.filter(
                sourcefiles__file_type=module.source_type,
                collections=collection).exclude(derivedfiles__module_version=version)
            for i, d in enumerate(docs, 1):
                logger.info("  document %s/%s - %s" % (i, len(docs), d))
                process_document.delay(d.pk, version.pk)


def get_essentia_hash():
    try:
        import essentia
        version = essentia.__version__
        sha = essentia.__version_git_sha__
        if '-g' in sha:
            sha = sha.rsplit('-g')[-1]
        return version, sha
    except ImportError:
        return None, None


def get_pycompmusic_hash():
    import compmusic._version
    version = compmusic._version.get_versions()
    return version['full-revisionid'], version['date']


@app.task
def register_host(hostname):
    ever, ehash = get_essentia_hash()
    if ever:
        essentia, created = models.EssentiaVersion.objects.get_or_create(version=ever, sha1=ehash)
    else:
        essentia = None
    phash, pdate = get_pycompmusic_hash()
    if phash and pdate:
        pycompmusic, created = models.PyCompmusicVersion.objects.get_or_create(sha1=phash, commit_date=pdate)
    else:
        pycompmusic = None

    worker, created = models.Worker.objects.get_or_create(hostname=hostname)
    worker.essentia = essentia
    worker.pycompmusic = pycompmusic
    worker.set_state_updated()
    worker.save()
