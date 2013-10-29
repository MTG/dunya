from docserver import models
from rest_framework import serializers

class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['name', 'description', 'slug', 'root_directory']

class DerivedFileSerializer(serializers.ModelSerializer):
    extension = serializers.Field(source='extension')
    versions = serializers.Field(source='versions')
    outputname = serializers.Field(source='outputname')
    numparts = serializers.Field(source='numparts')
    slug = serializers.Field(source='module_version.module.slug')

    class Meta:
        model = models.DerivedFile
        fields = ('extension', 'versions', 'outputname', 'numparts', 'slug')

class DocumentSerializer(serializers.ModelSerializer):
    # The extension field isn't part of a SourceFile, but we get it from the filetype
    sourcefiles = serializers.SlugRelatedField(many=True, slug_field='extension', read_only=True)
    #derivedfiles = serializers.SlugRelatedField(many=True, slug_field='extension', read_only=True)
    derivedfiles = DerivedFileSerializer(many=True)
    collection = serializers.CharField(max_length=100, source='collection.slug', read_only=True)
    class Meta:
        model = models.Document
        fields = ['collection', 'derivedfiles', 'sourcefiles', 'external_identifier', 'title']

class CollectionDetailSerializer(serializers.HyperlinkedModelSerializer):
    documents = DocumentSerializer(many=True)
    class Meta:
        model = models.Collection
        fields = ['name', 'documents']

class SourceFileSerializer(serializers.ModelSerializer):
    # TODO: Get file contents based on... document id & type, or alt id & type, or fileid
    class Meta:
        model = models.SourceFile
        fields = ('document', 'file_type', 'path')

