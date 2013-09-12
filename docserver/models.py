from django.db import models
from django_extensions.db.fields import UUIDField
from django.template.defaultfilters import slugify
from rest_framework import serializers
import django.utils.timezone

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

class CollectionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'slug', 'root_directory']


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

    def __unicode__(self):
        ret = ""
        if self.title:
            ret += "%s" % self.title
        if self.external_identifier:
            ret += " (%s)" % self.external_identifier
        return ret

class DocumentSerializer(serializers.ModelSerializer):
    sourcefiles = serializers.SlugRelatedField(many=True, slug_field='pk', read_only=True)
    derivedfiles = serializers.SlugRelatedField(many=True, slug_field='pk', read_only=True)
    class Meta:
        model = Document
        fields = ['collection', 'derivedfiles', 'sourcefiles', 'external_identifier', 'title']

class CollectionDetailSerializer(serializers.HyperlinkedModelSerializer):
    documents = DocumentSerializer(many=True)
    class Meta:
        model = Collection
        fields = ['name', 'documents']

class FileTypeManager(models.Manager):
    def get_by_extension(self, extension):
        extension = extension.lower()
        return self.get_query_set().get(extension=extension)

class SourceFileType(models.Model):
    objects = FileTypeManager()

    extension = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class SourceFile(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey("Document", related_name='sourcefiles')
    """The filetype"""
    file_type = models.ForeignKey(SourceFileType)
    """The path on disk to the file"""
    path = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s, %s)" % (self.document.title, self.file_type.name, self.path)

class SourceFileSerializer(serializers.ModelSerializer):
    # TODO: Get file contents based on... document id & type, or alt id & type, or fileid
    class Meta:
        model = SourceFile
        fields = ('document', 'file_type', 'path')

class DerivedFileType(models.Model):
    objects = FileTypeManager()

    extension = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=255)
    is_derived = models.BooleanField(default=False)
    derived_from_type = models.ForeignKey('SourceFileType', blank=True, null=True)

    def __unicode__(self):
        return self.name

class DerivedFile(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey("Document", related_name='derivedfiles')
    """The filetype"""
    file_type = models.ForeignKey(DerivedFileType)
    """The path on disk to the file"""
    path = models.CharField(max_length=200)
    derived_from = models.ForeignKey(SourceFile)
    module_version = models.ForeignKey("ModuleVersion")

    def __unicode__(self):
        return "%s (%s, %s)" % (self.document.title, self.file_type.name, self.path)

class DerivedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DerivedFile
        fields = ('document', 'file_type', 'path')

# Essentia management stuff

class EssentiaVersion(models.Model):
    version = models.CharField(max_length=200)
    sha1 = models.CharField(max_length=200)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    def __unicode__(self):
        return "Essentia %s (%s)" % (self.version, self.sha1)

class WorkerMachine(models.Model):
    name = models.CharField(max_length=200)
    hostname = models.CharField(max_length=200)
    moduleversions = models.ManyToManyField('ModuleVersion', through='WorkerMachineModuleVersion')
    essentiaversions = models.ManyToManyField('EssentiaVersion', through='WorkerMachineEssentiaVersion')

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.hostname)

class WorkerMachineEssentiaVersion(models.Model):
    essentiaversion = models.ForeignKey(EssentiaVersion)
    workermachine = models.ForeignKey(WorkerMachine)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

class Module(models.Model):
    name = models.CharField(max_length=200)
    path = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.path)

    def latest_version(self):
        versions = self.moduleversion_set.all()
        if len(versions):
            versions = sorted(versions, reverse=True)
            return versions[0].version
        else:
            return "(none)"

class ModuleVersion(models.Model):
    module = models.ForeignKey(Module)
    version = models.CharField(max_length=10)

    def __unicode__(self):
        return "v%s for %s" % (self.version, self.module)

class WorkerMachineModuleVersion(models.Model):
    workermachine = models.ForeignKey(WorkerMachine)
    moduleversion = models.ForeignKey(ModuleVersion)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

class RunResult(models.Model):
    date = models.DateTimeField(default=django.utils.timezone.now)
    essentiaversion = models.ForeignKey(EssentiaVersion)
    # TODO: Do we have a 'filetype' for each moduleversion? or just a single one?
    file = models.ForeignKey(DerivedFile)
    workermachine = models.ForeignKey(WorkerMachine)
    moduleversion = models.ForeignKey(ModuleVersion)
