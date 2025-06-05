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

import os
import re
import uuid

import compmusic
import requests.exceptions
from django import forms
from django.contrib.auth.models import User

import account.models
import data.models
import makam.models
from dashboard import models

uuid_match = r"(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})"


class CollectionForm(forms.Form):
    collectionid = forms.CharField(max_length=100, label="Musicbrainz collection ID")
    path = forms.CharField(max_length=200, label="Path to files on disk")
    do_import = forms.BooleanField(
        required=False, label="Import metadata into Dunya (in addition to loading into dashboard)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_path(self):
        pth = self.cleaned_data.get("path")
        if pth and not os.path.exists(pth):
            raise forms.ValidationError("This path doesn't exist")
        docserver_pth = os.path.join(pth, models.Collection.AUDIO_DIR)
        if not os.path.exists(docserver_pth):
            raise forms.ValidationError("Path doesn't contain inner 'audio'")
        return pth


class AddCollectionForm(CollectionForm):
    def clean_collectionid(self):
        """Check that the collectionid doesn't already exist in the DB"""
        cid = self.cleaned_data.get("collectionid")
        if cid:
            if not re.match(uuid_match, cid):
                raise forms.ValidationError("Collection ID needs to be a UUID")

            if models.Collection.objects.filter(collectionid=cid).exists():
                raise forms.ValidationError("A collection with this ID already exists")
        return cid

    def clean(self):
        cleaned_data = super().clean()
        collectionid = cleaned_data.get("collectionid")

        if collectionid:
            try:
                coll_name = compmusic.musicbrainz.get_collection_name(collectionid)
                cleaned_data["collectionname"] = coll_name
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 503:
                    raise forms.ValidationError("Error connecting to MusicBrainz, try again shortly")
                elif e.response.status_code == 404:
                    raise forms.ValidationError("Cannot find this collection on MusicBrainz")
                else:
                    raise forms.ValidationError("Unknown error connecting to MusicBrainz")

        return cleaned_data


class EditCollectionForm(CollectionForm):
    def __init__(self, collectionid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collectionid = collectionid
        self.fields["collectionid"].widget.attrs["readonly"] = True

    def clean(self):
        cleaned_data = super().clean()
        try:
            coll_name = compmusic.musicbrainz.get_collection_name(self.collectionid)
            cleaned_data["collectionname"] = coll_name
        except OSError:  # Probably an http 500 from MusicBrainz
            # If we had an error, don't worry, we'll just use the old name
            cleaned_data["collectionname"] = None

        return cleaned_data


class InactiveUserForm(forms.ModelForm):
    delete = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        # Construct a custom Form which includes the affiliation from the user profile
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.username = instance.username
            self.first_name = instance.first_name
            self.last_name = instance.last_name
            self.affiliation = instance.userprofile.affiliation
            self.email = instance.email

    class Meta:
        model = User
        fields = ["is_active"]


ACCESS_REQUEST_DECISION = [("approve", "Approve"), ("deny", "Deny")]


class AccessRequestApprovalForm(forms.ModelForm):
    decision = forms.ChoiceField(choices=ACCESS_REQUEST_DECISION, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        # Construct a custom Form which includes the affiliation from the user profile
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if instance and instance.pk:
            self.username = instance.user.username
            self.affiliation = instance.user.userprofile.affiliation
            self.justification = instance.justification

    class Meta:
        model = account.models.AccessRequest
        fields = ["id"]


class AccessCollectionForm(forms.ModelForm):
    class Meta:
        model = data.models.Collection
        exclude = ["name", "collectionid"]


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


class AndalusianScoreForm(forms.Form):
    score_file = forms.FileField()


class DashUUIDField(forms.UUIDField):
    """A UUIDField which returns uuids with dashes"""

    def prepare_value(self, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value


class SymbTrForm(forms.ModelForm):
    uuid = DashUUIDField()

    class Meta:
        model = makam.models.SymbTr
        fields = ["name", "uuid"]

    def clean_uuid(self):
        data = self.cleaned_data["uuid"]
        if "uuid" in self.changed_data or self.instance.pk is None:
            # If this is new, or if the uuid has changed, check if
            # there is already an object with this id
            if makam.models.SymbTr.objects.filter(uuid=data).exists():
                raise forms.ValidationError("UUID already exists")
        return data


class SymbTrFileForm(forms.Form):
    pdf = forms.FileField(required=False)
    txt = forms.FileField(required=False)
    mu2 = forms.FileField(required=False)
    xml = forms.FileField(required=False)
    midi = forms.FileField(required=False)
