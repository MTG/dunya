from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from dashboard import models
from dashboard import forms

def index(request):
    if request.method == 'POST':
        form = forms.AddCollectionForm(request.POST)
        if form.is_valid():
            # Import collection id
            coll_id = form.cleaned_data['collectionid']
            return HttpResponseRedirect(reverse('dashboard-home'))
    else:
        form = forms.AddCollectionForm()

    collections = models.MusicbrainzCollection.objects.all()
    ret = {'form': form, 'collections': collections}
    return render(request, 'dashboard/index.html', ret)

def collection(request, collectionid):
    pass

def release(request, releaseid):
    pass

def recording(request, recordingid):
    pass
