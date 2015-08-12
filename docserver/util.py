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

from docserver import models
import compmusic
import tempfile
import os
import subprocess
import json
from django.conf import settings

class NoFileException(Exception):
    pass

class TooManyFilesException(Exception):
    pass

def docserver_add_mp3(collectionid, releaseid, fpath, recordingid):
    meta = compmusic.file_metadata(fpath)
    mp3type = models.SourceFileType.objects.get_by_slug("mp3")
    title = meta["meta"].get("title")

    try:
        doc = models.Document.objects.get_by_external_id(recordingid)
        docserver_add_sourcefile(doc.pk, mp3type, fpath)
    except models.Document.DoesNotExist:
        docserver_add_document(collectionid, mp3type, title, fpath, recordingid)

def docserver_add_document(collection_id, filetype, title, path, alt_id=None):
    """ Add a document.
        Arguments:
          filetype: a SourceFileType
    """
    collection = models.Collection.objects.get(collectionid=collection_id)
    doc_collection = collection.get_default_doc_collection()
    document = models.Document.objects.create(rel_collections=doc_collection, title=title)
    if alt_id:
        document.external_identifier = alt_id
        document.save()
    docserver_add_sourcefile(document.pk, filetype, path)

def docserver_update_sourcefile(document_id, ftype, tmpefile, contents):
    pass

def docserver_add_sourcefile(document_id, ftype, path):
    """ Add a file to the given document. If a file with the given filetype
        already exists for the document just update the path and size. """
    document = models.Document.objects.get(pk=document_id)

    size = os.stat(path).st_size
    root_directory = os.path.join(document.get_absolute_path(), ftype.stype)
    if path.startswith(root_directory):
        # If the path is absolute, remove it
        path = path[len(root_directory):]
    if path.startswith("/"):
        path = path[1:]

    try:
        sfile = models.SourceFile.objects.get(document=document, file_type=ftype)
        sfile.path = path
        sfile.size = size
        sfile.save()
    except models.SourceFile.DoesNotExist:

        sfile = models.SourceFile.objects.create(document=document, file_type=ftype, path=path, size=size)

def docserver_get_wav_filename(documentid):
    """ Return a tuple (filename, created) containing the filename
        of a wave file for this document. If created is True, it means
        the file was generated on demand and you must delete it when
        you're finished. Otherwise it's from the docserver
    """
    try:
        filename = docserver_get_filename(documentid, "wav", "wave")
        if not os.path.exists(filename):
            raise NoFileException("Wave file doesn't exist")
        return filename, False
    except:  # Error getting file because it's not in the db or it doesn't exist
        print "Error getting file, calculating again"
        mp3filename = docserver_get_filename(documentid, "mp3")
        fp, tmpname = tempfile.mkstemp(".wav")
        os.close(fp)
        proclist = ["lame", "--decode", mp3filename, tmpname]
        p = subprocess.Popen(proclist)
        p.communicate()
        return tmpname, True

def docserver_get_url(documentid, slug, subtype=None, part=None, version=None):
    part = _docserver_get_part(documentid, slug, subtype, part, version)
    url = part.get_absolute_url()
    return url

def docserver_get_mp3_url(documentid):
    part = _docserver_get_part(documentid, "mp3")
    url = part.get_absolute_url("ds-download-mp3")
    return url

def docserver_get_filename(documentid, slug, subtype=None, part=None, version=None):
    part = _docserver_get_part(documentid, slug, subtype, part, version)
    derived_root = settings.AUDIO_ROOT
    file_path = part.path
    full_path = os.path.join(derived_root, file_path)
    return full_path

def _docserver_get_part(documentid, slug, subtype=None, part=None, version=None):
    try:
        doc = models.Document.objects.get(external_identifier=documentid)
    except models.Document.DoesNotExist:
        raise NoFileException("Cannot find a document with id %s" % documentid)
    try:
        sourcetype = models.SourceFileType.objects.get_by_slug(slug)
    except models.SourceFileType.DoesNotExist:
        sourcetype = None
    if doc and sourcetype:
        files = doc.sourcefiles.filter(file_type=sourcetype)
        if len(files) == 0:
            raise NoFileException("Looks like a sourcefile, but I can't find one")
        else:
            return files[0]

    try:
        module = models.Module.objects.get(slug=slug)
    except models.Module.DoesNotExist:
        raise NoFileException("Cannot find a module with type %s" % slug)
    moduleversions = module.versions
    if version:
        moduleversions = moduleversions.filter(version=version)
    else:
        moduleversions = moduleversions.order_by("-date_added")
    if len(moduleversions):
        dfs = None
        for mv in moduleversions:
            # go through all the versions until we find a file of that version
            dfs = doc.derivedfiles.filter(module_version=mv).all()
            if subtype:
                dfs = dfs.filter(outputname=subtype)
            if dfs.count() > 0:
                # We found some files, break
                break
        if dfs.count() > 1:
            raise TooManyFilesException("Found more than 1 subtype for this module but you haven't specified what you want")
        elif dfs.count() == 1:
            # Double-check if subtypes match. This is to catch the case where we
            # have only one subtype for a type but we don't specify it in the
            # query. By 'luck' we will get the right subtype, but this doesn't
            # preclude the default subtype changing in a future version.
            # Explicit is better than implicit
            derived = dfs.get()
            if derived.outputname != subtype:
                raise NoFileException("This module has only one subtype which you must specify (%s)" % (derived.outputname, ))
            # Select the part.
            # If the file has many parts and ?part is not set then it's an error
            parts = derived.parts
            if part:
                try:
                    part = int(part)
                    parts = parts.filter(part_order=part)
                except ValueError:
                    raise NoFileException("Invalid part")
            else:
                parts = parts.all()
            if parts.count() > 1:
                raise TooManyFilesException("Found more than 1 part without part set")
            elif parts.count() == 1:
                return parts[0]
            else:
                raise NoFileException("No parts on this file")
        else:
            # If no files, or none with this version
            msg = "No derived files with this type/subtype"
            if version:
                msg += " or version"
            raise NoFileException(msg)
    else:
        raise NoFileException("No known versions for this module")

def docserver_get_contents(documentid, slug, subtype=None, part=None, version=None):
    try:
        return open(docserver_get_filename(documentid, slug, subtype, part, version), "rb").read()
    except IOError:
        raise NoFileException

def docserver_get_json(documentid, slug, subtype=None, part=None, version=None):
    try:
        contents = open(docserver_get_filename(documentid, slug, subtype, part, version), "rb").read()
        return json.loads(contents)
    except IOError:
        raise NoFileException

def get_user_permissions(user):
    permission = ["U"]
    if user.is_staff:
        permission = ["S", "R", "U"]
    elif user.has_perm('docserver.access_restricted_file'):
        permission = ["R", "U"]
    return permission

def user_has_access(user, document, file_type):
    '''
    Returns True if the user has access to the source_file, this is made through 
    the related collection.
    Also returns True if there is no Source File with that slug but there is a Module.
    '''

    try:
        sourcetype = models.SourceFileType.objects.get_by_slug(file_type)
    except models.SourceFileType.DoesNotExist:
        sourcetype = None
    if not sourcetype:
        try:
            module = models.Module.objects.get(slug=file_type)
            return True
        except models.Module.DoesNotExist:
            return False
    
    user_permissions = get_user_permissions(user)
    return models.CollectionPermission.objects.filter(
            collection__in=document.rel_collections.collections.all(), source_type=sourcetype, permission__in=user_permissions).count() != 0
def has_rate_limit(user, document, file_type):
    '''
    Returns True if the user has access to the source_file with rate limit, 
    but if the user is staff always returns False
    '''
    user_permissions = get_user_permissions(user)
    for c in models.CollectionPermission.objects.filter(
            collection__in=document.rel_collections.collections.all(), source_type__slug=file_type, permission__in=user_permissions).all():
        if user.is_staff:
            return False
        return c.rate_limit
    return False


