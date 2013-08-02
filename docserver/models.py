from django.db import models
from django_extensions.db.fields import UUIDField
from rest_framework import serializers

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

class Document(models.Model):
    """An item in the collection.
    It has a known type and is part of a collection.
    It can be uniquely identified by a docid.
    It can have an option title and description
    """
    collection = models.ForeignKey(Collection, related_name='documents')
    docid = UUIDField(primary_key=True, default=new_uuid)
    title = models.CharField(max_length=200)

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
        fields = {'docid', 'title', 'files'}

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
    """If the file is known in a different database, the identifier
       for the item."""
    external_identifier = models.CharField(max_length=200)

class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('document', 'file_type', 'path', 'external_identifier')
