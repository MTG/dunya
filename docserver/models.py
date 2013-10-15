from django.db import models
from django_extensions.db.fields import UUIDField
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
import django.utils.timezone
import urlparse
import urllib

import uuid

class Collection(models.Model):
    """A set of related documents"""
    collectionid = UUIDField()
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    root_directory = models.CharField(max_length=200)

    def __unicode__(self):
        desc = "%s (%s)" % (self.name, self.slug)
        if self.description:
            desc += " - %s" % (self.description, )
        return desc

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Collection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("docserver-collection", args=[self.slug])


class DocumentManager(models.Manager):
    def get_by_external_id(self, external_id):
        return self.get_query_set().get(external_identifier=external_id)

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
        return reverse("docserver-onefile", args=[self.collection.slug, self.external_identifier])

    def __unicode__(self):
        ret = ""
        if self.title:
            ret += "%s" % self.title
        if self.external_identifier:
            ret += " (%s)" % self.external_identifier
        return ret


class FileTypeManager(models.Manager):
    def get_by_extension(self, extension):
        extension = extension.lower()
        return self.get_query_set().get(extension=extension)

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
    """The path on disk to the file"""
    path = models.CharField(max_length=500)

    @property
    def extension(self):
        return self.file_type.extension

    def get_absolute_url(self):
        return reverse("ds-download-external", 
                args=[self.document.external_identifier, self.file_type.extension])

    def __unicode__(self):
        return "%s (%s, %s)" % (self.document.title, self.file_type.name, self.path)

class DerivedFile(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey("Document", related_name='derivedfiles')
    """The path on disk to the file"""
    path = models.CharField(max_length=500)
    derived_from = models.ForeignKey(SourceFile)
    module_version = models.ForeignKey("ModuleVersion")

    #essentia_version = models.ForeignKey("EssentiaVersion")
    date = models.DateTimeField(default=django.utils.timezone.now)

    @property
    def versions(self):
        versions = self.module_version.module.moduleversion_set.all()
        return [v.version for v in versions]

    @property
    def extension(self):
        return self.module_version.module.slug

    def get_absolute_url(self):
        download_url = reverse("ds-download-external", 
                args=[self.document.external_identifier, self.extension])
        urlparts = list(urlparse.urlparse(download_url))
        urlparts[4] = urllib.urlencode({"v": self.module_version.version})
        download_url = urlparse.urlunparse(urlparts)
        return download_url

    def __unicode__(self):
        return "%s (%s, %s)" % (self.document.title, self.module_version.module.slug, self.path)

# Essentia management stuff

class EssentiaVersion(models.Model):
    version = models.CharField(max_length=200)
    sha1 = models.CharField(max_length=200)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    def __unicode__(self):
        return "Essentia %s (%s)" % (self.version, self.sha1)

class Module(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    module = models.CharField(max_length=200)
    source_type = models.ForeignKey(SourceFileType)

    collections = models.ManyToManyField(Collection)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.module)

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
        return "v%s for %s" % (self.version, self.module)

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

