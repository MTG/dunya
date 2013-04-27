from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from social.forms import *
from social.models import *
from datetime import datetime
from django.utils import simplejson

def main_page(request):
    return render_to_response('main_page.html',RequestContext(request))

def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404(u'Requested user not found.')

    fullname = user.get_full_name()

    variables = RequestContext(request, {
            'username': username,
            'fullname': fullname
    })
    return render_to_response('user_page.html', variables)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('carnatic-overview'))

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            
            user.save()
            
            return HttpResponseRedirect(reverse('social-auth-register-success'))
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
            'form': form
    })
    return render_to_response('registration/register.html',variables)

def tag_save_page(request):
    if request.method == 'POST':
        form = TagSaveForm(request.POST)
        if form.is_valid():
            # Create new tag list.
            objectid = int(form.cleaned_data['objectid'])
            tag_names = form.cleaned_data['tags'].split(",")
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name.lower(), category="") # tag to lower case
                artist = Artist.objects.get(pk=objectid)
                #artist.tag_set.add(tag)
                if len(ArtistTag.objects.filter(tag=tag, user=request.user, artist=artist)) == 0:
                    artist_tag, _ = ArtistTag.objects.get_or_create(tag=tag, user=request.user, artist=artist, timestamp=datetime.now())
            return HttpResponseRedirect('/carnatic/artist/%s' % objectid)
    else:
        form = TagSaveForm()
    variables = RequestContext(request, {
        'form': form
    })
    return render_to_response('form-tag.html', variables)


def user_profile(request):
    user_profile = request.user.get_profile()
    
    variables = RequestContext(request, {
        'user_profile': user_profile
    })
    return render_to_response('user-profile.html', variables)


def user_profile_save(request):
    user_profile = request.user.get_profile()
    if request.method == 'POST':
        form = UserProfileForm(request.POST)

    else:
        form = UserProfileForm()
    
    variables = RequestContext(request, {
        'user_profile': user_profile
    })
    return render_to_response('user-profile.html', variables)



def ajax_tag_autocomplete(request):
    q = request.GET['term']
    tags = Tag.objects.filter(name__istartswith=q)[:10]
    results = []
    for tag in tags:
        tag_dict = {'id':tag.id, 'label':tag.name, 'value':tag.name}
        results.append(tag_dict)
    return HttpResponse(simplejson.dumps(results),mimetype='application/json')






