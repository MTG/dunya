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

from django.shortcuts import get_object_or_404
from rest_framework import fields
from rest_framework import serializers

from docserver import models


class CollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['name', 'description', 'slug', 'root_directory', 'id']


class SourceFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SourceFile
        fields = ['document', 'file_type', 'path', 'size']


class DocumentSerializer(serializers.ModelSerializer):
    # The slug field isn't part of a SourceFile, but we get it from the filetype
    sourcefiles = serializers.SlugRelatedField(many=True, slug_field='slug', read_only=True)
    derivedfiles = fields.ReadOnlyField(source='derivedmap', read_only=True)
    collections = serializers.SlugRelatedField(many=True, slug_field='slug', read_only=True)

    class Meta:
        model = models.Document
        fields = ['collections', 'derivedfiles', 'sourcefiles', 'external_identifier', 'title']

    def create(self, validated_data):
        args = self.context["view"].kwargs
        collection = validated_data.pop('collection')
        get_object_or_404(models.Collection, **collection)
        external = args["external_identifier"]
        document, created = models.Document.objects.get_or_create(collections=collection, external_identifier=external, defaults=validated_data)
        return document


class DocumentIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ['external_identifier', 'title']


class CollectionDetailSerializer(serializers.HyperlinkedModelSerializer):
    documents = DocumentIdSerializer(many=True)

    class Meta:
        model = models.Collection
        fields = ['name', 'documents']
