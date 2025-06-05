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
import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.forms import modelform_factory
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.authtoken.models import Token

from account import forms
from account.models import AccessRequest
import dashboard.email


def register_page(request):
    if request.method == "POST":
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )
            user.is_active = False
            user.save()
            user.userprofile.affiliation = form.cleaned_data["affiliation"]
            user.userprofile.save()

            # send notification email to admin to review the account
            current_site = get_current_site(request)
            dashboard.email.email_admin_on_new_user(current_site, user)

            return HttpResponseRedirect(reverse("account-register-success"))
    else:
        form = forms.RegistrationForm()

    ret = {"form": form}
    return render(request, "registration/register.html", ret)


@login_required
def delete_account(request):
    if request.user.username == "guest":
        raise Http404
    if request.method == "POST":
        form = forms.DeleteAccountForm(request.POST)
        if form.is_valid():
            delete = form.cleaned_data["delete"]
            if delete:
                u = request.user
                logout(request)
                u.delete()
                return render(request, "registration/deleted.html")
    else:
        form = forms.DeleteAccountForm()

    ret = {"form": form}
    return render(request, "registration/delete.html", ret)


@login_required
def user_profile(request):
    if request.user.username == "guest":
        raise Http404
    user = request.user
    profile = user.userprofile
    token = Token.objects.get(user=request.user)
    initial = {
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "affiliation": profile.affiliation,
    }

    active_request = AccessRequest.objects.for_user(request.user)
    has_access_request = False
    if active_request and active_request.approved:
        has_access_request = True

    if request.method == "POST":
        form = forms.UserEditForm(request.POST, initial=initial)
        if form.is_valid() and form.has_changed():
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()
            profile.affiliation = form.cleaned_data["affiliation"]
            profile.save()
    else:
        form = forms.UserEditForm(initial=initial)

    ret = {"user_profile": user_profile, "token": token.key, "form": form, "has_access_request": has_access_request}
    return render(request, "account/user_profile.html", ret)


@login_required
def access_request(request):
    """Ask for access to restricted datasets"""
    AccessRequestForm = modelform_factory(AccessRequest, fields=("justification",))
    current_site = get_current_site(request)
    profile_url = reverse("account-user-profile")

    if request.user.username == "guest":
        return redirect(profile_url)

    active_request = AccessRequest.objects.for_user(request.user)
    if active_request:
        if active_request.approved is None:
            messages.add_message(
                request,
                messages.INFO,
                "You already have a pending access request. You will receive a notification when it is processed.",
            )
        return redirect(profile_url)

    if request.method == "POST":
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            user_request = form.save(commit=False)
            user_request.user = request.user
            user_request.save()
            dashboard.email.email_admin_on_access_request(current_site, request.user, user_request.justification)
            messages.add_message(
                request,
                messages.INFO,
                "Your access request has been received. You will receive a notification when it is processed.",
            )
            return redirect(profile_url)
    else:
        form = AccessRequestForm()

    ret = {"today": datetime.datetime.now().strftime("%Y-%m-%d"), "form": form}
    return render(request, "account/access_request.html", ret)
