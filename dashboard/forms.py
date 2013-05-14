from django import forms
import re

uuid_match = r'(?P<uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'

class AddCollectionForm(forms.Form):
    collectionid = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(AddCollectionForm, self).clean()
        cid = cleaned_data.get('collectionid')
        if cid:
            if not re.match(uuid_match, cid):
                raise forms.ValidationError("Needs to be a uuid")
        return cleaned_data
