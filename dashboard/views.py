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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.template import loader
from django.forms.models import modelformset_factory
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.contrib import messages

from dashboard import models
from dashboard import forms
from dashboard import jobs
import docserver

import compmusic
import os

import carnatic
import hindustani
import makam

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def addcollection(request):
    if request.method == 'POST':
        form = forms.AddCollectionForm(request.POST)
        if form.is_valid():
            # Import collection id
            coll_id = form.cleaned_data['collectionid']
            path = form.cleaned_data['path']
            coll_name = form.cleaned_data['collectionname']
            do_import = form.cleaned_data['do_import']
            checkers = []
            for i in form.cleaned_data['checkers']:
                checkers.append(get_object_or_404(models.CompletenessChecker, pk=int(i)))
            new_collection = models.Collection.objects.create(
                id=coll_id, name=coll_name,
                root_directory=path, do_import=do_import)
            new_collection.checkers.add(*checkers)
            docserver.models.Collection.objects.get_or_create(
                collectionid=coll_id,
                defaults={"root_directory": path, "name": coll_name})
            jobs.load_and_import_collection(new_collection.id)
            return redirect('dashboard-home')
    else:
        form = forms.AddCollectionForm()
    ret = {'form': form}
    return render(request, 'dashboard/addcollection.html', ret)

@user_passes_test(is_staff)
def index(request):

    collections = models.Collection.objects.all()
    ret = {'collections': collections}
    return render(request, 'dashboard/index.html', ret)

@user_passes_test(is_staff)
def accounts(request):
    UserFormSet = modelformset_factory(User, forms.InactiveUserForm, extra=0)
    print User.objects.filter(is_active=False).all()
    if request.method == 'POST':
        formset = UserFormSet(request.POST, queryset=User.objects.filter(is_active=False))
        if formset.is_valid():
            for f in formset.forms:
                user = f.cleaned_data["id"]
                is_active = f.cleaned_data["is_active"]
                if is_active:
                    user.is_active = True
                    user.save()

                    # send an email to the user notifying them that their account is active
                    subject = "Your Dunya account has been activated"
                    current_site = get_current_site(request)
                    context = {"username": user.username, "domain": current_site.domain}
                    message = loader.render_to_string('registration/email_account_activated.html', context)
                    from_email = settings.NOTIFICATION_EMAIL_FROM
                    recipients = [user.email, ]
                    send_mail(subject, message, from_email, recipients, fail_silently=True)

    formset = UserFormSet(queryset=User.objects.filter(is_active=False))
    ret = {"formset": formset}
    return render(request, 'dashboard/accounts.html', ret)

@user_passes_test(is_staff)
def delete_collection(request, uuid):
    c = get_object_or_404(models.Collection, pk=uuid)

    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete.lower().startswith("yes"):
            msg = "The collection %s is being deleted" % c.name
            messages.add_message(request, messages.INFO, msg)
            jobs.delete_collection.delay(c.pk)
            return redirect("dashboard-home")
        elif delete.lower().startswith("no"):
            return redirect("dashboard-collection", c.pk)

    ret = {"collection": c}
    return render(request, 'dashboard/delete_collection.html', ret)

@user_passes_test(is_staff)
def collection(request, uuid):
    c = get_object_or_404(models.Collection.objects.prefetch_related('collectionstate_set'), pk=uuid)

    rescan = request.GET.get("rescan")
    if rescan is not None:
        jobs.load_and_import_collection(c.id)
        return redirect('dashboard-collection', uuid)
    forcescan = request.GET.get("forcescan")
    if forcescan is not None:
        jobs.force_load_and_import_collection(c.id)
        return redirect('dashboard-collection', uuid)

    order = request.GET.get("order")
    releases = models.MusicbrainzRelease.objects.filter(collection=c)\
        .prefetch_related('musicbrainzreleasestate_set')\
        .prefetch_related('collectiondirectory_set')\
        .prefetch_related('collectiondirectory_set__collectionfile_set')
    if order == "date":
        def sortkey(rel):
            return rel.get_current_state().state_date
    elif order == "unmatched":
        def sortkey(rel):
            return (False if rel.matched_paths() else True, rel.get_current_state().state_date)
    elif order == "ignored":
        def sortkey(rel):
            return rel.ignore
    elif order == "error":
        def sortkey(rel):
            count = 0
            for state in rel.get_latest_checker_results():
                if state.result == 'b':
                    count += 1
            for directory in rel.collectiondirectory_set.all():
                for f in directory.collectionfile_set.all():
                    for state in f.get_latest_checker_results():
                        if state.result == 'b':
                            count += 1
            return count
    else:
        def sortkey(obj):
            pass
    releases = sorted(releases, key=sortkey, reverse=True)

    numfinished = sum(1 for _ in (r for r in releases if r.get_current_state().state == 'f'))
    numtotal = sum(1 for _ in (r for r in releases if len(r.all_files())))

    folders = models.CollectionDirectory.objects.filter(collection=c, musicbrainzrelease__isnull=True)
    log = models.CollectionLogMessage.objects.filter(collection=c).order_by('-datetime')
    ret = {"collection": c, "log_messages": log, "releases": releases,
           "folders": folders,
           "numtotal": numtotal, "numfinished": numfinished}
    return render(request, 'dashboard/collection.html', ret)

@user_passes_test(is_staff)
def release(request, releaseid):
    release = get_object_or_404(models.MusicbrainzRelease, pk=releaseid)

    reimport = request.GET.get("reimport")
    if reimport is not None:
        jobs.import_single_release.delay(release.id)
        return redirect('dashboard-release', releaseid)

    ignore = request.GET.get("ignore")
    if ignore is not None:
        release.ignore = True
        release.save()
        return redirect('dashboard-release', releaseid)
    unignore = request.GET.get("unignore")
    if unignore is not None:
        release.ignore = False
        release.save()
        return redirect('dashboard-release', releaseid)
    run = request.GET.get("run")
    if run is not None:
        module = int(run)
        # Get the recording ids in this release
        files = models.CollectionFile.objects.filter(directory__musicbrainzrelease=release)
        recids = [r.recordingid for r in files]
        docserver.jobs.run_module_on_recordings(module, recids)
        return redirect('dashboard-release', releaseid)

    files = release.collectiondirectory_set.order_by('path').all()
    log = release.musicbrainzreleaselogmessage_set.order_by('-datetime').all()

    allres = []
    results = release.get_latest_checker_results()
    for r in results:
        allres.append({"latest": r,
                       "others": release.get_rest_results_for_checker(r.checker.id)
                       })

    modules = docserver.models.Module.objects.all()
    ret = {"release": release, "files": files, "results": allres, "log_messages": log,
           "modules": modules}
    return render(request, 'dashboard/release.html', ret)

@user_passes_test(is_staff)
def file(request, fileid):
    thefile = get_object_or_404(models.CollectionFile, pk=fileid)
    log = thefile.collectionfilelogmessage_set.order_by('-datetime').all()

    allres = []
    results = thefile.get_latest_checker_results()
    for r in results:
        allres.append({"latest": r,
                       "others": thefile.get_rest_results_for_checker(r.checker.id)
                       })

    collection = thefile.directory.collection
    docid = thefile.recordingid
    docsrvcoll = docserver.models.Collection.objects.get(collectionid=collection.id)
    sourcefiles = []
    derivedfiles = []
    docsrvdoc = None
    try:
        docsrvdoc = docsrvcoll.documents.get(external_identifier=docid)
        sourcefiles = docsrvdoc.sourcefiles.all()
        derivedfiles = docsrvdoc.nestedderived()
    except docserver.models.Document.DoesNotExist:
        pass
    ret = {"file": thefile,
           "results": allres,
           "log_messages": log,
           "sourcefiles": sourcefiles,
           "derivedfiles": derivedfiles,
           "docsrvdoc": docsrvdoc}
    return render(request, 'dashboard/file.html', ret)

@user_passes_test(is_staff)
def directory(request, dirid):
    """ A directory that wasn't matched to a release in the collection.
    This could be because it has no release tags, or the release isn't in
    the collection.
    We want to group together as much common information as possible, and
    link to musicbrainz if we can.
    """
    directory = get_object_or_404(models.CollectionDirectory, pk=dirid)

    rematch = request.GET.get("rematch")
    if rematch is not None:
        # TODO: Change to celery
        jobs.rematch_unknown_directory(dirid)
        directory = get_object_or_404(models.CollectionDirectory, pk=dirid)
        return redirect('dashboard-directory', dirid)

    collection = directory.collection
    full_path = os.path.join(collection.root_directory, directory.path)
    files = os.listdir(full_path)
    releaseids = set()
    releasename = set()
    artistids = set()
    artistname = set()
    for f in files:
        fname = os.path.join(full_path, f)
        if compmusic.is_mp3_file(fname):
            data = compmusic.file_metadata(fname)
            relid = data["meta"]["releaseid"]
            relname = data["meta"]["release"]
            aname = data["meta"]["artist"]
            aid = data["meta"]["artistid"]
            if relid and relname:
                releaseids.add(relid)
                releasename.add(relname)
            if aname and aid:
                artistids.add(aid)
                artistname.add(aname)

    got_release_id = len(releaseids) == 1
    # TODO: This won't work if there are more than 1 lead artist?
    got_artist = len(artistids) == 1

    if directory.musicbrainzrelease:
        matched_release = directory.musicbrainzrelease
    else:
        matched_release = None

    ret = {"files": sorted(files), "directory": directory, "got_release_id": got_release_id, "got_artist": got_artist, "matched_release": matched_release}
    if got_release_id:
        ret["releasename"] = list(releasename)[0]
        ret["releaseid"] = list(releaseids)[0]
    if got_artist:
        ret["artistname"] = list(artistname)[0]
        ret["artistid"] = list(artistids)[0]
    return render(request, 'dashboard/directory.html', ret)

def _edit_attributedata(request, data):

    stylename = data["stylename"]
    entityname = data["entityname"]
    entityurl = data["entityurl"]
    klass = data["klass"]
    aliasklass = data["aliasklass"]
    template = data["template"]
    common_name = data.get("common_name", False)

    items = klass.objects.all()

    ret = {"items": items,
           "entityn": entityname,
           "entitynpl": "%ss" % entityname,
           "style": stylename,
           "entityurl": entityurl,
           "title": "%s editor" % entityname,
           "common_name": common_name,
           "alias": aliasklass
           }

    if request.method == 'POST':
        # Add aliases
        if aliasklass:
            for i in items:
                isadd = request.POST.get("item-%s-alias" % i.id)
                if isadd is not None:
                    i.aliases.create(name=isadd)
            # Delete alias
            for a in aliasklass.objects.all():
                isdel = request.POST.get("alias-rm-%s" % a.id)
                if isdel is not None:
                    a.delete()

        # Add new item
        refresh = False
        newname = request.POST.get("newname")
        newcommon = request.POST.get("newcommon")
        if newname is not None and newname != "":
            refresh = True
            args = {"name": newname}
            if common_name and newcommon is not None and newcommon != "":
                args["common_name"] = newcommon
            klass.objects.create(**args)
        # Delete item
        for i in items:
            isdel = request.POST.get("delete-item-%s" % i.id)
            if isdel is not None:
                refresh = True
                i.delete()
        if refresh:
            items = klass.objects.all()
            ret["items"] = items
    else:
        newname = request.GET.get("newname")
        if newname:
            ret["newname"] = newname

    return render(request, template, ret)

@user_passes_test(is_staff)
def carnatic_raagas(request):
    data = {"stylename": "Carnatic",
            "entityname": "Raaga",
            "entityurl": "dashboard-carnatic-raagas",
            "klass": carnatic.models.Raaga,
            "aliasklass": carnatic.models.RaagaAlias,
            "template": "dashboard/styletag.html",
            "common_name": True  # If this attribute has a common_name
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def carnatic_taalas(request):
    data = {"stylename": "Carnatic",
            "entityname": "Taala",
            "entityurl": "dashboard-carnatic-taalas",
            "klass": carnatic.models.Taala,
            "aliasklass": carnatic.models.TaalaAlias,
            "template": "dashboard/styletag.html",
            "common_name": True  # If this attribute has a common_name
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def carnatic_instruments(request):
    data = {"stylename": "Carnatic",
            "entityname": "Instrument",
            "entityurl": "dashboard-carnatic-instruments",
            "klass": carnatic.models.Instrument,
            "aliasklass": carnatic.models.InstrumentAlias,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)


@user_passes_test(is_staff)
def hindustani_raags(request):
    data = {"stylename": "Hindustani",
            "entityname": "Raag",
            "entityurl": "dashboard-hindustani-raags",
            "klass": hindustani.models.Raag,
            "aliasklass": hindustani.models.RaagAlias,
            "template": "dashboard/styletag.html",
            "common_name": True  # If this attribute has a common_name
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def hindustani_taals(request):
    data = {"stylename": "Hindustani",
            "entityname": "Taal",
            "entityurl": "dashboard-hindustani-taals",
            "klass": hindustani.models.Taal,
            "aliasklass": hindustani.models.TaalAlias,
            "template": "dashboard/styletag.html",
            "common_name": True  # If this attribute has a common_name
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def hindustani_layas(request):
    data = {"stylename": "Hindustani",
            "entityname": "Laya",
            "entityurl": "dashboard-hindustani-layas",
            "klass": hindustani.models.Laya,
            "aliasklass": hindustani.models.LayaAlias,
            "template": "dashboard/styletag.html",
            "common_name": True  # If this attribute has a common_name
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def hindustani_forms(request):
    data = {"stylename": "Hindustani",
            "entityname": "Form",
            "entityurl": "dashboard-hindustani-forms",
            "klass": hindustani.models.Form,
            "aliasklass": hindustani.models.FormAlias,
            "template": "dashboard/styletag.html",
            "common_name": True  # If this attribute has a common_name
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def hindustani_instruments(request):
    data = {"stylename": "Hindustani",
            "entityname": "Instrument",
            "entityurl": "dashboard-hindustani-instruments",
            "klass": hindustani.models.Instrument,
            "aliasklass": None,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def makam_makams(request):
    data = {"stylename": "Makam",
            "entityname": "Makam",
            "entityurl": "dashboard-makam-makams",
            "klass": makam.models.Makam,
            "aliasklass": makam.models.MakamAlias,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def makam_forms(request):
    data = {"stylename": "Makam",
            "entityname": "Form",
            "entityurl": "dashboard-makam-forms",
            "klass": makam.models.Form,
            "aliasklass": makam.models.FormAlias,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def makam_usuls(request):
    data = {"stylename": "Makam",
            "entityname": "Usul",
            "entityurl": "dashboard-makam-usuls",
            "klass": makam.models.Usul,
            "aliasklass": makam.models.UsulAlias,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)

@user_passes_test(is_staff)
def makam_instruments(request):
    data = {"stylename": "Makam",
            "entityname": "Instrument",
            "entityurl": "dashboard-makam-instruments",
            "klass": makam.models.Instrument,
            "aliasklass": None,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)
