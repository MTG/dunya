from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from social.forms import *


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
    return HttpResponseRedirect(reverse('social-main'))

def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            
            user.first_name=form.cleaned_data['first_name']
            user.last_name=form.cleaned_data['last_name']
            
            user.save()
            
            return HttpResponseRedirect(reverse('social-auth-register-success'))
    else:
        form = RegistrationForm()
    variables = RequestContext(request, {
            'form': form
    })
    return render_to_response('registration/register.html',variables)

