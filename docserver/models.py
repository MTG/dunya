from django.db import models
from django_extensions.db.fields import UUIDField
from rest_framework import serializers
import django.utils.timezone

import uuid

class Collection(models.Model):
    """A set of related documents"""
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    root_dir = models.CharField(max_length=200)

    def __unicode__(self):
        desc = "%s (%s)" % (self.name, self.slug)
        if self.description:
            desc += " - %s" % (self.description, )
        return desc

class CollectionListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'slug', 'root_dir']

class CollectionDetailSerializer(serializers.HyperlinkedModelSerializer):
    documents = serializers.SlugRelatedField(many=True, slug_field='docid')
    class Meta:
        model = Collection
        fields = ['name', 'description', 'slug', 'root_dir', 'documents']

def new_uuid():
    u = uuid.uuid4()
    return str(u)

class DocumentManager(models.Manager):
    def get_by_external_id(self, external_id):
        return self.get_query_set().get(external_identifier=external_id)

class Document(models.Model):
    """An item in the collection.
    It has a known type and is part of a collection.
    It can be uniquely identified by a docid.
    It can have an option title and description
    """

    objects = DocumentManager()

    collection = models.ForeignKey(Collection, related_name='documents')
    docid = UUIDField(primary_key=True, default=new_uuid)
    title = models.CharField(max_length=200)
    """If the file is known in a different database, the identifier
       for the item."""
    external_identifier = models.CharField(max_length=200, blank=True, null=True)

    def get_document_by_fileid(self, fileid):
        """Some files (e.g. recordings) have an external ID
           (e.g., recording mbid). Get the document that has 
           a file with this id set
        """
        pass

class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    files = serializers.PrimaryKeyRelatedField(many=True)
    class Meta:
        model = Document
        fields = ('docid', 'title', 'files', 'external_identifier')

class FileType(models.Model):
    extension = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=255)
    is_derived = models.BooleanField(default=False)
    derived_from = models.ForeignKey('FileType', blank=True, null=True)

    def __unicode__(self):
        return self.name

class File(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey(Document, related_name='files')
    """The filetype"""
    file_type = models.ForeignKey(FileType)
    """The path on disk to the file"""
    path = models.CharField(max_length=200)

class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
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
    file = models.ForeignKey(File)
    workermachine = models.ForeignKey(WorkerMachine)
    moduleversion = models.ForeignKey(ModuleVersion)
