import importlib
import os
import json

from docserver import models
import celery

from django.conf import settings

def _get_module_instance_by_path(modulepath):
    mod, clsname = modulepath.rsplit(".", 1)
    package = importlib.import_module(mod)
    cls = getattr(package, clsname)
    return cls()

def create_module(modulepath):
    instance = _get_module_instance_by_path(modulepath)
    try:
        sourcetype = models.SourceFileType.objects.get(extension=instance.__sourcetype__)
    except models.SourceFileType.DoesNotExist as e:
        raise Exception("Cannot find source file type '%s'" % instance.__sourcetype__, e)

    module = models.Module.objects.create(name=modulepath.rsplit(".", 1)[1],
                    slug=instance.__slug__,
                    module=modulepath,
                    source_type=sourcetype)
    get_latest_module_version(module)

def get_latest_module_version(themod=None):
    if themod:
        modules = [themod]
    else:
        modules = models.Module.objects.all()
    for m in modules:
        instance = _get_module_instance_by_path(m.module)
        version = instance.__version__
        v = "%s" % version

        versions = m.moduleversion_set.filter(version=version)
        if not len(versions):
            models.ModuleVersion.objects.create(module=m, version=v)

def _save_file(collection, recording, slug, data):
    fdir = os.path.join(settings.AUDIO_ROOT, collection, recording)
    try:
        os.makedirs(fdir)
    except OSError:
        pass
    fname = "%s.json" % slug

    fullname = os.path.join(fdir, fname)
    fp = open(fullname, "wb")
    json.dump(data, fp)
    return fullname

@celery.task
def process_document(documentid, moduleversionid):
    version = models.ModuleVersion.objects.get(pk=moduleversionid)
    module = version.module
    instance = _get_module_instance_by_path(module.module)

    document = models.Document.objects.get(pk=documentid)

    sfiles = document.sourcefiles.filter(file_type=module.source_type)
    if len(sfiles):
        s = sfiles[0]
        fname = s.path.encode("utf-8")
        result = instance.run(fname)

        collectionid = document.collection.collectionid
        moduleslug = module.slug
        result_name = _save_file(collectionid, document.external_identifier, moduleslug, result)
        # TODO: What if this file for this version already exists?
        df = models.DerivedFile.objects.create(document=document, path=result_name, derived_from=s,
                module_version=version)
        return df
    else:
        return None

def run_module_on_collection(collectionslug, moduleslug):
    collection = models.Collection.objects.get(slug=collectionslug)
    module = models.Module.objects.get(slug=moduleslug)
    version = module.get_latest_version()
    if version:
        docs = models.Document.objects.filter(sourcefile__file_type=module.source_type).exclude(derivedfiles__module_version=version)
        for d in docs:
            # TODO: Delay
            process_document(d.pk, version.pk)
