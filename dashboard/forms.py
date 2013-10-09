from django import forms
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


