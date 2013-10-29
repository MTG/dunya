from docserver import models
import compmusic

def docserver_add_mp3(collectionid, releaseid, fpath, recordingid):
    meta = compmusic.file_metadata(fpath)
    # TODO: We assume it's MP3 for now.
    mp3type = models.SourceFileType.objects.get_by_extension("mp3")
    title = meta["meta"].get("title")

    try:
        doc = models.Document.objects.get_by_external_id(recordingid)
        docserver_add_file(doc.pk, mp3type, fpath)
    except models.Document.DoesNotExist:
        docserver_add_document(collectionid, mp3type, title, fpath, recordingid)

def docserver_add_document(collection_id, filetype, title, path, alt_id=None):
    collection = models.Collection.objects.get(collectionid=collection_id)
    document = models.Document.objects.create(collection=collection, title=title)
    if alt_id:
        document.external_identifier = alt_id
        document.save()
    docserver_add_file(document.pk, filetype, path)

def docserver_add_file(document_id, ftype, path):
    """ Add a file to the given document. If a file with the given filetype
        already exists for the document just update the path. """
    document = models.Document.objects.get(pk=document_id)
    try:
        sfile = models.SourceFile.objects.get(document=document, file_type=ftype)
        sfile.path = path
        sfile.save()
    except models.SourceFile.DoesNotExist:
        sfile = models.SourceFile.objects.create(document=document, file_type=ftype, path=path)

def docserver_get_url(documentid, slug, subtype=None, part=None, version=None):
    part = _docserver_get_part(documentid, slug, subtype, part, version)
    url = part.get_absolute_url()
    return url

def docserver_get_filename(documentid, slug, subtype=None, part=None, version=None):
    part = _docserver_get_part(documentid, slug, subtype, part, version)
    return part.path

def _docserver_get_part(documentid, slug, subtype=None, part=None, version=None):
    doc = models.Document.objects.get(external_identifier=documentid)
    module = models.Module.objects.get(slug=slug)
    moduleversions = module.moduleversion_set
    if version:
        moduleversions = moduleversions.filter(version=version)
    else:
        moduleversions = moduleversions.order_by("-date_added")
    if len(moduleversions):
        mv = moduleversions[0]
        dfs = doc.derivedfiles.filter(module_version=mv).all()
        if subtype:
            dfs = dfs.filter(outputname=subtype)
        if dfs.count() > 1:
            raise Exception("Found more than 1 outputname per this modver without a subtype set")
        elif dfs.count() == 1:
            # Select the part.
            # If the file has many parts and ?part is not set then it's an error
            parts = dfs[0].parts
            if part:
                parts = parts.filter(part_order=int(part))
            else:
                parts = parts.all()
            if parts.count() > 1:
                raise Exception("Found more than 1 part without part set")
            elif parts.count() == 1:
                return parts[0]
            else:
                raise Exception("Can't find")
        else:
            # If no files, or none with this version
            raise Exception("Can't find")
    else:
        raise Exception("Can't find")

def docserver_get_contents(documentid, slug, subtype=None, part=None, version=None):
    return open(docserver_get_filename(documentid, slug, subtype, part, version), "rb").read()

