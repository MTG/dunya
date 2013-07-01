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

    collections = models.Collection.objects.all()
    ret = {'form': form, 'collections': collections}
    return render(request, 'dashboard/index.html', ret)

def collection(request, uuid):
    c = models.Collection.objects.get(pk=uuid)
    log = models.CollectionLogMessage.objects.filter(collection=c)
    releases = models.MusicbrainzRelease.objects.filter(collection=c)
    folders = models.CollectionDirectory.objects.filter(collection=c, musicbrainz_release__isnull=True)
    ret = {"collection": c, "log_messages": log, "releases": releases, "folders": folders}
    return render(request, 'dashboard/collection.html', ret)

def release(request, uuid):
    return render(request, 'dashboard/release.html')

def recording(request, recordingid):
    pass
