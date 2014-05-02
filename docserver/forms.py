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

from docserver import models

class EssentiaVersionForm(forms.ModelForm):
    class Meta:
        model = models.EssentiaVersion
        fields = ["version", "sha1", "date_added"]

class ModuleEditForm(forms.ModelForm):
    class Meta:
        model = models.Module
        fields = ["collections"]
        widgets = {'collections': forms.CheckboxSelectMultiple()}

class ModuleForm(forms.Form):
    module = forms.CharField()
    
    def __init__(self, *args, **kwargs):
        super(ModuleForm, self).__init__(*args, **kwargs)

        choices = []
        for checker in models.Collection.objects.all():
            choices.append( (checker.pk, checker.name) )

        self.fields['collections'] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=choices)

    class Meta:
        fields = []
