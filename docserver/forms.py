from django import forms

from docserver import models

class EssentiaVersionForm(forms.ModelForm):
    class Meta:
        model = models.EssentiaVersion

class ModuleForm(forms.ModelForm):
    class Meta:
        model = models.Module
