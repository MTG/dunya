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

class JsonForm(forms.Form):
    json_file = forms.FileField()
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=None)

    def clean_json_file(self):
        # Validate that is a json file and size is less than the specified
        content = self.cleaned_data['json_file']
        content_type = content.content_type.split('/')[1]
        if content_type in ["json"]:
            if content._size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Please keep filesize under %s. Current filesize %s' % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(content._size)))
        else:
            raise forms.ValidationError('File type is not supported')
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
        # Select the items with the same id
        existent_items = Item.objects.filter(ref__in=self.new_items_dic.keys(), category=self.cleaned_data['category'])
        for item in existent_items:
            for field in self.new_items_dic[item.ref]:
                old_field = item.fields.filter(key=field.key)
                # If the old Fields have the same key, override the value unless they have been already modified
                if len(old_field) == 1 and old_field[0].value != field.value and not old_field[0].modified:
                    old_field[0].value = field.value
                    old_filed[0].save()
                elif len(old_field) == 0:
                    field.item = item
                    field.save()
            del self.new_items_dic[item.ref]
        # Save the new Fields and Items
        for ref, fields in self.new_items_dic.iteritems():
            item = Item(ref=ref)
            item.category = self.cleaned_data['category']
            item.save()
            for field in fields:
                field.item = item
                field.save()

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
    
    def save(self, commit=True):
        self.instance.modified = True
        return super(FieldForm, self).save(commit)
