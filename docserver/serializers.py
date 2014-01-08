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

