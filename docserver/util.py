from docserver import models

def docserver_add_document(collection_id, filetype, title, path, alt_id=None):
    collection = models.Collection.objects.get(pk=collection_id)
    document = models.Document.objects.create(collection=collection, title=title)
    if alt_id:
        document.external_identifier = alt_id
        document.save()
    docserver_add_file(document.id, filetype, path)

def docserver_add_file(document_id, filetype, path):
    document = models.Document.objects.get(pk=document_id)

    ftype = models.File.objects.get(extension=filetype)
    file = models.File.objects.create(document=document, file_type=ftype, path=path)

def docserver_add_contents(collection_id, document_id, fileytpe, title, contents):
    collection = models.Collection.objects.get(pk=collection_id)
