from django import forms

from docserver import models

class EssentiaVersionForm(forms.ModelForm):
    class Meta:
        model = models.EssentiaVersion

class ModuleForm(forms.Form):
    module = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)

        choices = []
        for checker in models.Collection.objects.all():
            choices.append( (checker.pk, checker.name) )

        self.fields['collections'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)
