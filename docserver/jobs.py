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
import shutil
import logging
import time
import subprocess

from dashboard.log import logger
from docserver import models
from docserver import log
import numpy as np

from django.conf import settings
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
                models.DocumentLogMessage.objects.create(document=doc, moduleversion=modv, sourcefile=sourcef, level=record.levelname, message=record.getMessage())
            except models.Document.DoesNotExist:
                logger.error("no document, can't create a log file")
        else:
            logger.error("no document, can't create a log file")

#logger = logging.getLogger("extractor")
#logger.setLevel(logging.DEBUG)
#logger.addHandler(DatabaseLogHandler())

def _get_module_instance_by_path(modulepath):
    args = {}
    try:
        redis_host = settings.WORKER_REDIS_HOST
        args = {"redis_host": redis_host}
    except AttributeError:
        pass
    #try:
    mod, clsname = modulepath.rsplit(".", 1)
    print mod, clsname
    package = importlib.import_module(mod)
    cls = getattr(package, clsname)
    return cls(**args)
    #except ImportError:
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
            if m.disabled: # if we were disabled and exist again, reenable.
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
        for p in f.parts.all():
            path = p.fullpath
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
    if module.versions.count() == 0:
        logger.info("No more moduleversions for this module, deleting the module")
        module.delete()
        logger.info(" .. module deleted")
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

    dfparts = models.DerivedFilePart.objects.filter(derivedfile__document__collections__in=collections)
    paths = [f.fullpath for f in dfparts]
    for f in paths:
        os.remove(f)
    collection.delete()

class NumPyArangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # or map(int, obj)
        return json.JSONEncoder.default(self, obj)

def _save_file(root_directory, recordingid, version, slug, partslug, partnumber, extension, data):
    recordingstub = recordingid[:2]
    reldir = os.path.join(recordingstub, recordingid, slug, version)
    fdir = os.path.join(root_directory, settings.DERIVED_FOLDER, reldir)
    try:
        os.makedirs(fdir)
    except OSError:
        logger.warn("Error making directory %s" % fdir)
        pass
    fname = "%s-%s-%s-%s-%s.%s" % (recordingid, slug, version, partslug, partnumber, extension)

    fullname = os.path.join(fdir, fname)
    fullrelname = os.path.join(reldir, fname)
    try:
        fp = open(fullname, "wb")
        if extension == "json":
            json.dump(data, fp, cls=NumPyArangeEncoder)
        else:
            if not isinstance(data, basestring):
                logger.warn("Data is not a string-ish thing. instead it's %s" % type(data))
            fp.write(data)
        fp.close()
    except OSError:
        logger.warn("Error writing to file %s" % fullname)
        logger.warn("Probably a permissions error")
        return None, None, None
    if not isinstance(data, basestring):
        data = str(data)
    return fullname, fullrelname, len(data)

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
    moduleslug = module.slug
    with transaction.atomic():
        for dataslug, contents in results.items():
            outputdata = instance._output[dataslug]
            extension = outputdata["extension"]
            mimetype = outputdata["mimetype"]
            multipart = outputdata.get("parts", False)
            logger.info("data %s (%s)" % (dataslug, type(contents)))
            logger.info("multiparts %s" % multipart)
            df = models.DerivedFile.objects.create(
                document=document,
                module_version=version, outputname=dataslug, extension=extension,
                mimetype=mimetype, computation_time=total_time)
            if worker:
                df.essentia = worker.essentia
                df.pycompmusic = worker.pycompmusic
                df.save()

            if not multipart:
                contents = [contents]
            for i, partdata in enumerate(contents, 1):
                saved_name, rel_path, saved_size = _save_file(
                    document.get_root_dir(), document.external_identifier,
                    version.version, moduleslug, dataslug, i, extension, partdata)
                if saved_name:
                    df.save_part(i, rel_path, saved_size)

    # When we've finished, log that we processed the file. If this throws an
    # exception, we won't do the log.
    log.log_processed_file(instance.hostname, document.external_identifier, version.pk)


@app.task
def process_collection(collectionid, moduleversionid):
    version = models.ModuleVersion.objects.get(pk=moduleversionid)
    module = version.module
    instance = _get_module_instance_by_path(module.module)

    hostname = process_document.request.hostname
    worker = _get_worker_from_hostname(hostname)

    instance.hostname = hostname
    # if the extractor run over all the collection then the document
    # has the same id of the collection and the result is
    # set to this document

    collection = models.Collection.objects.get(pk=collectionid)
    results = None
    sfiles = models.SourceFile.objects.filter(document__collections=collection, file_type=module.source_type)

    document, created = models.Document.objects.get_or_create(pk=collectionid,
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
    results = None
    sfiles = document.sourcefiles.filter(file_type=module.source_type)
    if len(sfiles):
        s = sfiles[0]
        fname = s.fullpath.encode("utf-8")
        starttime = time.time()
        results = instance.process_document(document.pk, s.pk, document.external_identifier, fname)
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


ESSENTIA_DIR = "/srv/essentia"
COMPMUSIC_DIR = "/srv/dunya/env/src/pycompmusic"

def get_git_hash(cwd):
    proc = subprocess.Popen("git rev-parse HEAD", cwd=cwd, stdout=subprocess.PIPE, shell=True)
    version = proc.communicate()[0].strip()
    proc = subprocess.Popen("git log -1 --format=%ci", cwd=cwd, stdout=subprocess.PIPE, shell=True)
    date = proc.communicate()[0].strip()
    # Git puts a space before timezone identifier, but django doesn't like it
    date = date.replace(" +", "+").replace(" -", "-")
    return version, date

def get_pycompmusic_hash():
    return get_git_hash(COMPMUSIC_DIR)

def get_essentia_hash():
    return get_git_hash(ESSENTIA_DIR)

def get_essentia_version():
    import essentia
    return essentia.__version__

@app.task
def register_host(hostname):
    try:
        # Some machines don't have essentia
        ever = get_essentia_version()
        ehash, edate = get_essentia_hash()
        essentia, created = models.EssentiaVersion.objects.get_or_create(version=ever, sha1=ehash, commit_date=edate)
    except OSError:
        essentia = None
    phash, pdate = get_pycompmusic_hash()
    pycompmusic, created = models.PyCompmusicVersion.objects.get_or_create(sha1=phash, commit_date=pdate)

    worker, created = models.Worker.objects.get_or_create(hostname=hostname)
    worker.essentia = essentia
    worker.pycompmusic = pycompmusic
    worker.set_state_updated()
    worker.save()

def git_update_and_compile_essentia():
    subprocess.call("git checkout deploy", cwd=ESSENTIA_DIR, shell=True)
    subprocess.call("git fetch --all", cwd=ESSENTIA_DIR, shell=True)
    subprocess.call("git reset --hard origin/deploy", cwd=ESSENTIA_DIR, shell=True)
    subprocess.call("./waf -v", cwd=ESSENTIA_DIR, shell=True)
    subprocess.call("./waf install", cwd=ESSENTIA_DIR, shell=True)

def git_update_pycompmusic():
    subprocess.call("git fetch --all", cwd=COMPMUSIC_DIR, shell=True)
    subprocess.call("git reset --hard origin/master", cwd=COMPMUSIC_DIR, shell=True)

@app.task
def update_essentia(hostname):
    worker = models.Worker.objects.get(hostname=hostname)
    worker.set_state_updating()
    git_update_and_compile_essentia()
    ever = get_essentia_version()
    ehash, edate = get_essentia_hash()
    version, created = models.EssentiaVersion.objects.get_or_create(version=ever, sha1=ehash, commit_date=edate)
    worker.essentia = version
    worker.set_state_updated()
    worker.save()

@app.task
def update_pycompmusic(hostname):
    worker = models.Worker.objects.get(hostname=hostname)
    worker.set_state_updating()
    git_update_pycompmusic()
    phash, pdate = get_pycompmusic_hash()
    version, created = models.PyCompmusicVersion.objects.get_or_create(sha1=phash, commit_date=pdate)
    worker.pycompmusic = version
    worker.set_state_updated()
    worker.save()

    if hostname == "sitar":
        # Special case. If we upgrade pycompmusic on sitar, the webserver,
        # make sure we scan for new versions of all extractors.
        get_latest_module_version()

def shutdown_celery(hostname):
    name = "celery@%s" % hostname
    app.control.broadcast("shutdown", destination=[name])

@app.task
def update_single_worker(hostname):
    try:
        # Some workers don't have essentia
        update_essentia(hostname)
    except OSError:
        pass
    update_pycompmusic(hostname)
    shutdown_celery(hostname)

def update_all_workers(user=None):
    workers = models.Worker.objects.all()
    for w in workers:
        log.log_worker_action(w.hostname, user, "updateall")
        update_single_worker.apply_async([w.hostname], queue=w.hostname)
