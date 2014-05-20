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

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.template import loader
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from social.forms import *
from social.models import *
from datetime import datetime
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.utils.http import urlunquote_plus
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.contrib.sites.models import get_current_site

import json
import social.timeline as timeline
from django.core.mail import send_mail

def main_page(request):
    return render(request, "social/main_page.html")

def logout_page(request):
    logout(request)
    if request.GET.has_key("next"):
        return HttpResponseRedirect(request.GET['next'])
    return HttpResponseRedirect(reverse('carnatic-main'))

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
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
            user.userprofile.affiliation=form.cleaned_data['affiliation']
            user.userprofile.save()

            # send notification email to admin to review the account
            subject = "New user registration - %s" % user.username
            current_site = get_current_site(request)
            context = {"username": user.username, "domain": current_site.domain}
            message = loader.render_to_string('registration/email_notify_admin.html', context)
            from_email = settings.NOTIFICATION_EMAIL_FROM
            recipients = [a for a in settings.NOTIFICATION_EMAIL_TO]
            send_mail(subject, message, from_email, recipients, fail_silently=True)

            return HttpResponseRedirect(reverse('social-auth-register-success'))
    else:
        form = RegistrationForm()

    ret = {
        'form': form
    }
    return render(request, 'registration/register.html', ret)

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            delete = form.cleaned_data['delete']
            if delete:
                u = request.user
                logout(request)
                u.delete()
                return render(request, 'registration/deleted.html')
    else:
        form = DeleteAccountForm()

    ret = {"form": form}
    return render(request, 'registration/delete.html', ret)


@login_required
def user_profile(request):
    user_profile = request.user.get_profile()

    users_id = []
    users_id.append(request.user.id)

    timelines = timeline.timeline(users_id)
    token = Token.objects.get(user=request.user)

    ret = {
        'user_profile': user_profile,
        'token': token.key
    }
    return render(request, 'social/user-profile.html', ret)

def users_list(request):
    numusers = User.objects.count()
    users = User.objects.all()

    ret = {"numusers": numusers,
           "users": users,
           }
    return render(request, "social/users_list.html", ret)

def user_page(request, username):
    other_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(UserProfile, user_id=other_user.id)

    user = request.user
    if len(UserFollowsUser.objects.filter(user_follower_id=user, user_followed_id=other_user)) == 0:
        follow = False
    else:
        follow = True

    users_id = []
    users_id.append(other_user.id)
    timelines = timeline.timeline(users_id)

    ret = {"other_user": other_user,
           "profile": profile,
           "timeline": timelines,
           "follow": follow
    }

    return render(request, "social/user_page.html", ret)

def timeline_page(request):
    follower = request.user
    users_followed = UserFollowsUser.objects.filter(user_follower=follower).values('user_followed_id')
    users_id = []
    users_id.append(request.user.id)

    for user in users_followed:
        users_id.append(user['user_followed_id'])

    timelines = timeline.timeline(users_id)

    ret = {
        'timeline': timelines
    }
    return render(request, 'social/timeline-page.html', ret)

@csrf_protect
def user_follow(request):
    to_follow = get_object_or_404(User, username=request.POST['username'])
    follower = request.user
    user_follows_user, _ = UserFollowsUser.objects.get_or_create(user_follower=follower, user_followed=to_follow, timestamp=datetime.now())
    ret = {"status": "OK"}
    return HttpResponse(json.dumps(ret), content_type="application/json")

@csrf_protect
def user_unfollow(request):
    to_unfollow = get_object_or_404(User, username=request.POST['username'])
    follower = request.user
    print follower, to_unfollow
    user_follows_user = UserFollowsUser.objects.filter(user_follower=follower, user_followed=to_unfollow)
    if len(user_follows_user) == 0:
        ret = {"status": "FAIL"}
    else:
        user_follows_user.delete()
        ret = {"status": "OK"}
    return HttpResponse(json.dumps(ret), content_type="application/json")

##### TAG ####

def tag_save_page(request):
    if request.method == 'POST':
        form = TagSaveForm(request.POST)
        if form.is_valid():
            # Create new tag list.
            objectid = int(form.cleaned_data['objectid'])
            objecttype = form.cleaned_data['objecttype'].lower()
            tag_names = form.cleaned_data['tags'].split(",")
            for tag_name in tag_names:
                if len(tag_name) > 0:
                    tag, _ = Tag.objects.get_or_create(name=tag_name.lower().strip()) # tag to lower case
                    if len(Annotation.objects.filter(tag=tag, user=request.user, entity_type=objecttype, entity_id=objectid)) == 0:
                        object_tag, _ = Annotation.objects.get_or_create(tag=tag, user=request.user, entity_type=objecttype, entity_id=objectid)

            return HttpResponseRedirect('/carnatic/%s/%s' % (objecttype, objectid))
    else:
        form = TagSaveForm()

    ret = {
        'form': form
    }
    return render(request, 'social/form-tag.html', ret)


def ajax_tag_autocomplete(request):
    q = request.GET['term']
    tags = Tag.objects.filter(name__istartswith=q)[:10]
    results = []
    for tag in tags:
        tag_dict = {'id':tag.id, 'label':tag.name, 'value':tag.name}
        results.append(tag_dict)
    return HttpResponse(json.dumps(results),mimetype='application/json')


def __get_entity(entity_type, entity_id):
    if entity_type == "artist":
        return Artist.objects.get(pk=entity_id)
    elif entity_type == "concert":
        return Concert.objects.get(pk=entity_id)
    elif entity_type == "recording":
        return Recording.objects.get(pk=entity_id)
    elif entity_type == "work":
        return Work.objects.get(pk=entity_id)
    return None

def tag_page(request, tagname, modeltype="concert"):
    tagname = urlunquote_plus(tagname)
    tag = get_object_or_404(Tag, name=tagname)

    lists = Annotation.objects.filter(tag__name=tagname, entity_type=modeltype).values('entity_type', 'entity_id', 'tag').annotate(freq=Count('entity_type'))
    objects=[]
    for lista in lists:
        objects.append([__get_entity(modeltype, lista['entity_id']), lista['freq']])

    ret = {
        'objects': objects,
        'tag_name': tagname,
        'modeltype': modeltype,
    }
    return render(request, 'social/tag_page.html', ret)

