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
import json

from django import forms
from django.conf import settings

from kvedit.models import Field, Item, Category
from kvedit import utils

class JsonForm(forms.Form):
    json_file = forms.FileField()
    category = forms.CharField()

    def clean_json_file(self):
        # Validate that is a json file and size is less than the specified
        content = self.cleaned_data['json_file']
        if content._size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('Please keep filesize under %s. Current filesize %s' % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        return content

    def clean(self):
        cleaned_data = super(JsonForm, self).clean()
        if 'json_file' in cleaned_data:
            new_items = json.load(cleaned_data['json_file'])
            if not isinstance(new_items, list):
                raise forms.ValidationError('The Json file must contain a list of elements')

            new_items_dic = {}
            for i in new_items:
                if "id" not in i.keys():
                    raise forms.ValidationError('All the elements must contain an "id" key, error at: %s ...' % str(i)[:45] )
                #Fill map with the id as the key and the values as the Field objects
                for k,v in i.iteritems():
                    if k != "id":
                        if i['id'] not in new_items_dic:
                            new_items_dic[i['id']] = []
                        new_items_dic[i['id']].append(Field(key=k, value=v))
            self.new_items_dic = new_items_dic

    def save(self, commit=True):
        utils.upload_kvdata(self.cleaned_data['category'], self.new_items_dic)

class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        exclude = ['item']

    def __init__(self, *args, **kwargs):
        super(FieldForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['key'].widget.attrs['readonly'] = True
            self.fields['value'].widget.attrs['rows'] = 4
            self.fields['value'].widget.attrs['cols'] = 75
