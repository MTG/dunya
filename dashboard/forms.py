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

from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
import re
import os

import data
import compmusic

from dashboard import models

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

class CollectionForm(forms.Form):
    collectionid = forms.CharField(max_length=100, label="Musicbrainz collection ID")
    path = forms.CharField(max_length=200, label="Path to files on disk")
    do_import = forms.BooleanField(required=False)
    bootleg = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)

        choices = []
        for checker in models.CompletenessChecker.objects.all():
            choices.append((checker.pk, checker.name))
        self.ccheckers = choices

        self.fields['checkers'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)


    def clean_path(self):
        pth = self.cleaned_data.get('path')
        if pth and not os.path.exists(pth):
            raise forms.ValidationError("This path doesn't exist")
        docserver_pth = os.path.join(pth, "audio")
        if not os.path.exists(docserver_pth):
            raise forms.ValidationError("Path doesn't contain inner 'audio'")
        return pth


class AddCollectionForm(CollectionForm):

    def clean_collectionid(self):
        """ Check that the collectionid doesn't already exist in the DB """
        cid = self.cleaned_data.get('collectionid')
        if cid:
            if not re.match(uuid_match, cid):
                raise forms.ValidationError("Collection ID needs to be a UUID")

            if models.Collection.objects.filter(id=cid).exists():
                raise forms.ValidationError("A collection with this ID already exists")
        return cid

    def clean(self):
        cleaned_data = super(AddCollectionForm, self).clean()
        collectionid = cleaned_data.get('collectionid')

        if collectionid:

            try:
                coll_name = compmusic.musicbrainz.get_collection_name(collectionid)
                cleaned_data['collectionname'] = coll_name
            except compmusic.musicbrainz.urllib2.HTTPError as e:
                if e.code == 503:
                    raise forms.ValidationError("Error connecting to MusicBrainz, try again shortly")
                elif e.code == 404:
                    raise forms.ValidationError("Cannot find this collection on MusicBrainz")
                else:
                    raise forms.ValidationError("Unknown error connecting to MusicBrainz")

        return cleaned_data

class EditCollectionForm(CollectionForm):
    def __init__(self, collectionid, *args, **kwargs):
        super(EditCollectionForm, self).__init__(*args, **kwargs)
        self.collectionid = collectionid
        self.fields['collectionid'].widget.attrs['readonly'] = True

    def clean(self):
        """ Check that the collectionid doesn't already exist in the DB """
        cleaned_data = super(CollectionForm, self).clean()
        try:
            coll_name = compmusic.musicbrainz.get_collection_name(self.collectionid)
            cleaned_data['collectionname'] = coll_name
        except IOError:  # Probably an http 500
            # If we had an error, don't worry, we'll just use the old name
            cleaned_data['collectionname'] = None

        return cleaned_data


class InactiveUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InactiveUserForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.username = instance.username
            self.first_name = instance.first_name
            self.last_name = instance.last_name
            self.affiliation = instance.userprofile.affiliation
            self.email = instance.email

    class Meta:
        model = User
        fields = ['is_active']

class AccessCollectionForm(forms.ModelForm):
    class Meta:
        model = data.models.Collection
        exclude = ['name']

OPTIONS = (
            ("tabs", "Tabs"),
            ("nawbas", "Nawbas"),
            ("forms", "Forms"),
            ("mizans", "Mizans"),
          )
class CsvAndalusianForm(forms.Form):
    csv_file = forms.FileField()
    elem_type = forms.ChoiceField(choices=OPTIONS)
class CsvAndalusianCatalogForm(forms.Form):
    csv_file = forms.FileField()

