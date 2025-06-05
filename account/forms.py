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

import re

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrationForm(forms.Form):
    required_css_class = "required"
    username = forms.CharField(label="Username", max_length=30)
    first_name = forms.CharField(label="First name", max_length=30)
    last_name = forms.CharField(label="Last name", max_length=30)
    affiliation = forms.CharField(label="Affiliation", max_length=100)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Password (Again)", widget=forms.PasswordInput())

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already taken.")
        return email

    def clean_affiliation(self):
        affiliation = self.cleaned_data["affiliation"]
        if affiliation == "":
            raise ValidationError("Affiliation must be entered")
        return affiliation

    def clean_password2(self):
        if "password1" in self.cleaned_data:
            password1 = self.cleaned_data["password1"]
            password2 = self.cleaned_data["password2"]
            if password1 == password2:
                return password2
        raise forms.ValidationError("Passwords do not match.")

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re.search(r"^[\w.]+$", username):
            raise forms.ValidationError("Username can only contain alphanumeric characters and the underscore.")
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("Username is already taken.")


class DeleteAccountForm(forms.Form):
    delete = forms.BooleanField(required=False, label="Yes, delete my account")


class UserEditForm(forms.Form):
    email = forms.CharField(label="Email address", max_length=200)
    first_name = forms.CharField(label="First Name", max_length=50)
    last_name = forms.CharField(label="Last Name", max_length=100)
    affiliation = forms.CharField(label="Affiliation", max_length=100)
