from django import forms

class AddCollectionForm(forms.Form):
    collectionid = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(AddCollectionForm, self).clean()
        cid = cleaned_data.get('collectionid')
        if cid:
            if cid != "hello":
                raise forms.ValidationError("Needs to be a uuid")
        return cleaned_data
