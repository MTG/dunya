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

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.template import loader
from rest_framework.authtoken.models import Token

from account import forms


def register_page(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            user.is_active = False
            user.save()
            user.userprofile.affiliation = form.cleaned_data['affiliation']
            user.userprofile.save()

            # send notification email to admin to review the account
            subject = "New user registration - %s" % user.username
            current_site = get_current_site(request)
            context = {"username": user.username, "domain": current_site.domain}
            message = loader.render_to_string('registration/email_notify_admin.html', context)
            from_email = settings.NOTIFICATION_EMAIL_FROM
            recipients = [a for a in settings.NOTIFICATION_EMAIL_TO]
            send_mail(subject, message, from_email, recipients, fail_silently=True)

            return HttpResponseRedirect(reverse('account-register-success'))
    else:
        form = forms.RegistrationForm()

    ret = {
        'form': form
    }
    return render(request, 'registration/register.html', ret)


@login_required
def delete_account(request):
    if request.user.username == "guest":
        raise Http404
    if request.method == 'POST':
        form = forms.DeleteAccountForm(request.POST)
        if form.is_valid():
            delete = form.cleaned_data['delete']
            if delete:
                u = request.user
                logout(request)
                u.delete()
                return render(request, 'registration/deleted.html')
    else:
        form = forms.DeleteAccountForm()

    ret = {"form": form}
    return render(request, 'registration/delete.html', ret)


@login_required
def user_profile(request):
    if request.user.username == "guest":
        raise Http404
    user = request.user
    profile = user.userprofile
    token = Token.objects.get(user=request.user)
    initial = {"email": user.email, "first_name": user.first_name,
               "last_name": user.last_name, "affiliation": profile.affiliation}

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

    ret = {
        'user_profile': user_profile,
        'token': token.key,
        'form': form
    }
    return render(request, 'account/user_profile.html', ret)
