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
from django.contrib.auth.models import User
import re
import os

import compmusic

from dashboard import models

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

class AddCollectionForm(forms.Form):
    collectionid = forms.CharField(max_length=100, label="Musicbrainz collection ID")
    path = forms.CharField(max_length=200, label="Path to files on disk")
    do_import = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(AddCollectionForm, self).__init__(*args, **kwargs)

        choices = []
        for checker in models.CompletenessChecker.objects.all():
            choices.append( (checker.pk, checker.name) )

        self.fields['checkers'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)


    def clean_collectionid(self):
        cid = self.cleaned_data.get('collectionid')
        if cid:
            if not re.match(uuid_match, cid):
                raise forms.ValidationError("Collection ID needs to be a UUID")
        return cid

    def clean_path(self):
        pth = self.cleaned_data.get('path')
        if pth:
            if not os.path.exists(pth):
                raise forms.ValidationError("This path doesn't exist")
        return pth

    def clean(self):
        """ Check that the collectionid doesn't already exist in the DB """
        cleaned_data = super(AddCollectionForm, self).clean()
        collectionid = cleaned_data['collectionid']

        if models.Collection.objects.filter(id=collectionid).count() > 0:
            raise forms.ValidationError("A collection with this ID already exists")

        try:
            coll_name = compmusic.musicbrainz.get_collection_name(collectionid)
            cleaned_data['collectionname'] = coll_name
        except IOError: # Probably an http 500
            raise forms.ValidationError("Cannot find this collection on MusicBrainz")

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
