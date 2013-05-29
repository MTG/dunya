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

    @property
    def files(self):
        pass

    def get_file_by_extension(self, ext):
        """Get the file for this document that has the given extension"""
        pass

    def get_conversions(self):
        """Return a list of file types that exist for this document"""
        pass

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
    is_derived = models.BooleanField()
    derived_from = models.ForeignKey('FileType')

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
    """A field to uniquely identify many files of the same type that
       belong to a single document (e.g. 2 analysis features)"""
    disambiguation = models.CharField(max_length=500)

    def get_conversions(self):
        pass

class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('document', 'file_type', 'path', 'external_identifier')

class FileConverter(models.Model):
    """Some documents can be transformed on the fly from one
    format to another, e.g., flac to ogg.
    A FileConverter specifies the class that knows how
    to convert a file type into any other compatible type.
    """
    to_type = models.ForeignKey(FileType)
    description = models.CharField(max_length=200)
    conversion_class = models.CharField(max_length=200)
