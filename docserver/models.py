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

from django.db import models
from django.conf import settings
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import django.utils.timezone
import urlparse
import urllib
import collections
import os

import uuid

class Collection(models.Model):
    """A set of related documents"""
    collectionid = UUIDField()
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    root_directory = models.CharField(max_length=200)

    def __unicode__(self):
        desc = u"%s (%s)" % (self.name, self.slug)
        if self.description:
            desc += u" - %s" % (self.description, )
        return desc

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Collection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("docserver-collection", args=[self.slug])


class DocumentManager(models.Manager):
    def get_by_external_id(self, external_id):
        return self.get_queryset().get(external_identifier=external_id)

class Document(models.Model):
    """An item in the collection.
    It has a known title and is part of a collection.
    It can have an option title and description
    """

    objects = DocumentManager()

    collection = models.ForeignKey(Collection, related_name='documents')
    title = models.CharField(max_length=200)
    """If the file is known in a different database, the identifier
       for the item."""
    external_identifier = models.CharField(max_length=200, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("ds-document-external", args=[self.external_identifier])

    def __unicode__(self):
        ret = u""
        if self.title:
            ret += u"%s" % self.title
        if self.external_identifier:
            ret += u" (%s)" % self.external_identifier
        return ret

    def derivedmap(self):
        """ Derived files for the API.
        returns {"slug": {"part": {"versions", [versions], "extension"...} ]}

        This makes an assumption that the number of parts and extension
        are the same for all versions. At the moment they are, but
        I'm not sure what to do if 
        """
        ret = collections.defaultdict(list)
        derived = self.derivedfiles.all()
        for d in derived:
            item = {"extension": d.extension, "version": d.module_version.version, 
                    "outputname": d.outputname, "numparts": d.numparts,
                    "mimetype": d.mimetype}
            ret[d.module_version.module.slug].append(item)
        newret = {}
        for k, v in ret.items():
            items = collections.defaultdict(list)
            for i in v:
                name = i['outputname']
                if name in items:
                    items[name]["versions"].append(i["version"])
                else:
                    items[name] = {"extension": i["extension"], 
                            "numparts": i["numparts"],
                            "mimetype": i["mimetype"],
                            "versions": [i["version"]]}

            newret[k] = items
        return newret


class FileTypeManager(models.Manager):
    def get_by_extension(self, extension):
        extension = extension.lower()
        return self.get_queryset().get(extension=extension)

class SourceFileType(models.Model):
    objects = FileTypeManager()

    extension = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class SourceFile(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey(Document, related_name='sourcefiles')
    """The filetype"""
    file_type = models.ForeignKey(SourceFileType)
    """The relative path on disk to the file (to the collection root)"""
    path = models.CharField(max_length=500)
    size = models.IntegerField()

    @property
    def extension(self):
        return self.file_type.extension

    def get_absolute_url(self, url_slug='ds-download-external'):
        return reverse(url_slug,
                args=[self.document.external_identifier, self.file_type.extension])

    @property
    def fullpath(self):
        return os.path.join(self.document.collection.root_directory, self.path)

    @property
    def mimetype(self):
        # TODO: For now all source files are mp3, but this won't be for long
        return "audio/mpeg"

    def __unicode__(self):
        return u"%s (%s, %s)" % (self.document.title, self.file_type.name, self.path)

class DerivedFilePart(models.Model):
    derivedfile = models.ForeignKey("DerivedFile", related_name='parts')
    part_order = models.IntegerField()
    path = models.CharField(max_length=500)
    size = models.IntegerField()

    @property
    def mimetype(self):
        return self.derivedfile.mimetype

    @property
    def fullpath(self):
        return os.path.join(settings.AUDIO_ROOT, self.path)

    def get_absolute_url(self, url_slug='ds-download-external'):
        url = reverse(url_slug,
            args=[self.derivedfile.document.external_identifier, self.derivedfile.module_version.module.slug ])
        v = self.derivedfile.module_version.version
        sub = self.derivedfile.outputname
        part = self.part_order
        url = "%s?part=%s&v=%s&subtype=%s" % (url, part, v, sub)
        return url

    def __unicode__(self):
        ret = u"%s: path %s" % (self.derivedfile, self.path)
        if self.part_order:
            ret = u"%s - part %s" % (ret, self.part_order)
        return ret

class DerivedFile(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey("Document", related_name='derivedfiles')
    """The path on disk to the file"""
    derived_from = models.ForeignKey(SourceFile)

    # A module could output more than 1 file. The combination of
    # module_version and (outputname/extension) refers to one
    # unique file output.
    module_version = models.ForeignKey("ModuleVersion")
    outputname = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    mimetype = models.CharField(max_length=100)
    computation_time = models.IntegerField(blank=True, null=True)

    #essentia_version = models.ForeignKey("EssentiaVersion")
    date = models.DateTimeField(default=django.utils.timezone.now)

    def save_part(self, part_order, path, size):
        """Add a part to this file"""
        return DerivedFilePart.objects.create(derivedfile=self, part_order=part_order, path=path, size=size)

    @property
    def versions(self):
        versions = self.module_version.module.moduleversion_set.all()
        return [v.version for v in versions]

    @property
    def numparts(self):
        return self.parts.count()

    def get_absolute_url(self):
        url = reverse("ds-download-external",
                args=[self.document.external_identifier, self.module_version.module.slug])
        v = self.module_version.version
        sub = self.outputname
        url = "%s?v=%s&subtype=%s" % (url, v, sub)
        return url

    def __unicode__(self):
        return u"%s (%s/%s)" % (self.document.title, self.module_version.module.slug, self.outputname)


# Essentia management stuff

class EssentiaVersion(models.Model):
    version = models.CharField(max_length=200)
    sha1 = models.CharField(max_length=200)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    def __unicode__(self):
        return u"Essentia %s (%s)" % (self.version, self.sha1)

class Module(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    depends = models.CharField(max_length=100, blank=True, null=True)
    module = models.CharField(max_length=200)
    source_type = models.ForeignKey(SourceFileType)

    collections = models.ManyToManyField(Collection)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.module)

    def processed_files(self):
        latest = self.get_latest_version()
        all_collections = self.collections.all()
        qs = Document.objects.filter(collection__in=all_collections,
                sourcefiles__file_type=self.source_type)
        if latest:
            qs = qs.filter(derivedfiles__module_version=self.get_latest_version())
        else:
            # If we don't have a version we probably can't show files yet
            return []
        return qs

    def unprocessed_files(self):
        latest = self.get_latest_version()
        all_collections = self.collections.all()
        qs = Document.objects.filter(collection__in=all_collections,
                sourcefiles__file_type=self.source_type)
        if latest:
            qs = qs.exclude(derivedfiles__module_version=self.get_latest_version())
        else:
            return []
        return qs

    def latest_version_number(self):
        version = self.get_latest_version()
        if version:
            return version.version
        else:
            return "(none)"

    def get_latest_version(self):
        versions = self.moduleversion_set.order_by("-date_added")
        if len(versions):
            return versions[0]
        else:
            return None

class ModuleVersion(models.Model):
    module = models.ForeignKey(Module)
    version = models.CharField(max_length=10)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    def __unicode__(self):
        return u"v%s for %s" % (self.version, self.module)

class DocumentLogMessage(models.Model):
    """ A log message about a document. Normally the log message refers to ModuleVersion
    processing a specific SourceFile, but these can be blank """

    class Meta:
        ordering = ['-datetime']

    document = models.ForeignKey(Document, related_name="logs")
    moduleversion = models.ForeignKey(ModuleVersion, blank=True, null=True)
    sourcefile = models.ForeignKey(SourceFile, blank=True, null=True)
    level = models.CharField(max_length=20)
    message = models.TextField()
    datetime = models.DateTimeField(default=django.utils.timezone.now)

