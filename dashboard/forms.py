from django import forms
import re
import os

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

class AddCollectionForm(forms.Form):
    collectionid = forms.CharField(max_length=100, label="Musicbrainz collection ID")
    path = forms.CharField(max_length=200, label="Path to files on disk")

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
