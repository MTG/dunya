from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from dashboard import models
from dashboard import forms
import compmusic
import os

def index(request):
    if request.method == 'POST':
        form = forms.AddCollectionForm(request.POST)
        if form.is_valid():
            # Import collection id
            coll_id = form.cleaned_data['collectionid']
            path = form.cleaned_data['path']
            coll_name = compmusic.musicbrainz.get_collection_name(coll_id)
            models.Collection.objects.create(id=coll_id, name=coll_name, root_directory=path)
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
    release = models.MusicbrainzRelease.objects.get(pk=uuid)
    files = release.collectiondirectory_set.all()

    ret = {"release": release, "files": files}
    return render(request, 'dashboard/release.html', ret)

def file(request, fileid):
    return render(request, 'dashboard/file.html')

def directory(request, dirid):
    """ A directory that wasn't matched to a release in the collection.
    This could be because it has no release tags, or the release isn't in
    the collection.
    We want to group together as much common information as possible, and
    link to musicbrainz if we can.
    """

    directory = models.CollectionDirectory.objects.get(pk=dirid)
    collection = thedir.collection
    full_path = os.path.join(collection.root_directory, thedir.path)
    files = os.listdir(full_path)
    meta = {}
    releaseids = []
    releasename = []
    artistids = []
    artistname = []
    for f in files:
        data = compmusic.file_metadata(os.path.join(full_path, f))
        meta[f] = data

    ret = {"files": meta, "directory": directory}
    return render(request, 'dashboard/directory.html', ret)
