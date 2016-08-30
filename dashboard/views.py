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
import csv

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.template import loader
from django.forms.models import modelformset_factory
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

from dashboard import models
from dashboard import forms
from dashboard import jobs
import docserver
import docserver.util

import compmusic
import os
import time

from mishkal.tashkeel.tashkeel import TashkeelClass
from ALA_LC_Transliterator import ALA_LC_Transliterator
import arabic_reshaper

import andalusian
import carnatic
import hindustani
import makam
import data

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def editcollection(request, uuid):
    collection = get_object_or_404(models.Collection, pk=uuid)
    if request.method == 'POST':
        data = {'collectionid': uuid,
                'path': request.POST.get("path"),
                'do_import': request.POST.get("do_import"),
                }
        form = forms.EditCollectionForm(uuid, data)
        if form.is_valid():
            coll_id = form.cleaned_data['collectionid']
            path = form.cleaned_data['path']
            coll_name = form.cleaned_data['collectionname']
            do_import = form.cleaned_data['do_import']

            if coll_name and coll_name != collection.name:
                collection.name = coll_name
            collection.do_import = do_import
            collection.root_directory = path
            collection.save()

            doccoll = docserver.models.Collection.objects.get(collectionid=coll_id)
            if coll_name and coll_name != doccoll.name:
                doccoll.name = coll_name
            doccoll.root_directory = path
            doccoll.save()
            return redirect('dashboard-collection', uuid)
    else:
        data = {'collectionid': uuid,
                'path': collection.root_directory,
                'do_import': collection.do_import,
                }
        form = forms.EditCollectionForm(uuid, data)
    ret = {'form': form}
    return render(request, 'dashboard/editcollection.html', ret)

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
            dashboard_root = os.path.join(path, models.Collection.AUDIO_DIR)
            new_collection = models.Collection.objects.create(
                id=coll_id, name=coll_name,
                root_directory=dashboard_root, do_import=do_import)
            docserver_coll, created = docserver.models.Collection.objects.get_or_create(
                collectionid=coll_id,
                defaults={"root_directory": path, "name": coll_name})
            if not created:
                docserver_coll.root_directory = path
                docserver_coll.name = coll_name
                docserver_coll.save()
            data_coll, created = data.models.Collection.objects.get_or_create(
                mbid=coll_id,
                defaults={"name": coll_name})
            if not created:
                data_coll.name = coll_name
                data_coll.save()
            jobs.force_load_and_import_collection(new_collection.id)
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
def delete_database_files(request, uuid):
    c = get_object_or_404(models.Collection, pk=uuid)

    if request.method == "POST":
        delete = request.POST.get("delete")
        if delete.lower().startswith("yes"):
            c.collectiondirectory_set.all().delete()
            return redirect("dashboard-home")
        elif delete.lower().startswith("no"):
            return redirect("dashboard-collection", c.pk)

    ret = {"collection": c}
    return render(request, 'dashboard/delete_collection_db_files.html', ret)

@user_passes_test(is_staff)
def collection(request, uuid):
    c = get_object_or_404(models.Collection.objects.prefetch_related('collectionstate_set'), pk=uuid)

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

    numtotal = len(releases)
    numfinished = 0
    nummatched = 0
    for r in releases:
        if r.all_files():
            nummatched += 1
            if r.get_current_state().state == 'f':
                numfinished += 1

    folders = models.CollectionDirectory.objects.filter(collection=c, musicbrainzrelease__isnull=True)
    log = models.CollectionLogMessage.objects.filter(collection=c).order_by('-datetime')
    ret = {"collection": c, "log_messages": log, "releases": releases,
           "folders": folders,
           "numtotal": numtotal, "numfinished": numfinished, "nummatched": nummatched}
    return render(request, 'dashboard/collection.html', ret)

@user_passes_test(is_staff)
def release(request, releaseid):
    release = get_object_or_404(models.MusicbrainzRelease, pk=releaseid)

    reimport = request.GET.get("reimport")
    if reimport is not None:
        jobs.import_single_release.delay(release.id)
        return redirect('dashboard-release', releaseid)

    delete = request.GET.get("delete")
    if delete is not None:
        collection = release.collection
        release.delete()
        return redirect('dashboard-collection', collection.pk)

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

    modules = docserver.models.Module.objects.all()
    ret = {"release": release, "files": files, "log_messages": log,
           "modules": modules}
    return render(request, 'dashboard/release.html', ret)

@user_passes_test(is_staff)
def file(request, fileid):
    thefile = get_object_or_404(models.CollectionFile, pk=fileid)

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
def carnatic_forms(request):
    data = {"stylename": "Carnatic",
            "entityname": "Form",
            "entityurl": "dashboard-carnatic-forms",
            "klass": carnatic.models.Form,
            "aliasklass": carnatic.models.FormAlias,
            "template": "dashboard/styletag.html",
            }

    return _edit_attributedata(request, data)

def carnatic_artists_list(request):
    data = {"artists": carnatic.models.Artist.objects.order_by('name').filter(dummy=False),
            "entityurl": "dashboard-carnatic-artist",
            "template": "dashboard/edit_artist_list.html",
           }
    return _edit_artists_list(request, data)

@user_passes_test(is_staff)
def carnatic_artist_desc(request, artistid):
    artist = get_object_or_404(carnatic.models.Artist, id = artistid)
    return _edit_artist_desc(request, artist, entityurl= "dashboard-carnatic-artist")

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
def hindustani_artists_list(request):
    data = {"artists": hindustani.models.Artist.objects.order_by('name').all(),
            "entityurl": "dashboard-hindustani-artist",
            "template": "dashboard/edit_artist_list.html",
           }
    return _edit_artists_list(request, data)

@user_passes_test(is_staff)
def hindustani_artist_desc(request, artistid):
    artist = get_object_or_404(hindustani.models.Artist, id = artistid)
    return _edit_artist_desc(request, artist, entityurl="dashboard-hindustani-artist")

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

@user_passes_test(is_staff)
def makam_symbtrlist(request):
    symbtr = makam.models.SymbTr.objects.all()
    ret = {"symbtr": symbtr}
    return render(request, "dashboard/makam_symbtrlist.html", ret)

def _get_symbtr_sourcetypes():
    types = [u'symbtrtxt', u'symbtrmidi', u'symbtrpdf', u'symbtrxml', u'symbtrmu2']
    return docserver.models.SourceFileType.objects.filter(slug__in=types)

@user_passes_test(is_staff)
def makam_symbtr(request, uuid=None):
    """
      - Add new mapping
        - Create document if it doesn't exist
      - Rename mapping
        - Rename document name  (if not taksim)
        - If uuid changes, make or get document
          - Copy symbtr source files from old to new
          - Delete old document if no other sourcefiles
      - Upload symbtr file
        - Get name, copy in, create/get sourcefile, attach to document
    """
    if uuid:
        symbtr = get_object_or_404(makam.models.SymbTr, uuid=uuid)
        delete = request.GET.get("delete")
        if delete == "1":
            symbtr.delete()
            return redirect('dashboard-makam-symbtrlist')
        is_taksim = "taksim" in symbtr.name
        if is_taksim:
            mbtype = "recording"
        else:
            mbtype = "work"
        url = "https://musicbrainz.org/%s/%s" % (mbtype, symbtr.uuid)
    else:
        is_taksim = False
        symbtr = None
        url = ""

    if request.method == 'POST':
        form = forms.SymbTrForm(request.POST, instance=symbtr)
        if form.is_valid():
            form.save()
            newuuid = form.instance.uuid
            newdoc, created = docserver.models.Document.objects.get_or_create(
                    external_identifier=newuuid, defaults={"title": form.instance.name})
            collection = docserver.models.Collection.objects.get(slug="makam-symbtr")
            docserver.util.docserver_create_document(collection.collectionid, newuuid, form.instance.name)
            if not created and not is_taksim:
                newdoc.title = form.instance.name
                newdoc.save()
            if uuid != form.instance.uuid:
                # Copy from old document to new document
                if uuid:
                    olddoc = docserver.models.Document.objects.get(external_identifier=uuid)
                    sfs = olddoc.sourcefiles.filter(file_type__in=_get_symbtr_sourcetypes())
                    for s in sfs:
                        s.document = newdoc
                        s.save()
                    olddoc = docserver.models.Document.objects.get(external_identifier=uuid)
                    if olddoc.sourcefiles.count() == 0:
                        olddoc.delete()
                return redirect('dashboard-makam-symbtr', form.instance.uuid)
            symbtr = get_object_or_404(makam.models.SymbTr, uuid=uuid)
            # If main data form is valid, this one was unused
            symbtrfiles = forms.SymbTrFileForm()


        symbtrfiles = forms.SymbTrFileForm(request.POST, request.FILES)
        if symbtrfiles.is_valid():
            pref = "symbtr"
            for f in ['txt', 'midi', 'xml', 'pdf', 'mu2']:
                fdata = symbtrfiles.files.get(f)
                if fdata:
                    stypename = pref + f
                    stype = docserver.models.SourceFileType.objects.get_by_slug(stypename)
                    doc = docserver.models.Document.objects.get(external_identifier=uuid)
                    docserver.util.docserver_upload_and_save_file(doc.id, stype.id, fdata)

    else:
        form = forms.SymbTrForm(instance=symbtr)
        symbtrfiles = forms.SymbTrFileForm()

    existing = {}
    if uuid:
        doc = docserver.models.Document.objects.get(external_identifier=uuid)
        sfs = doc.sourcefiles.filter(file_type__in=_get_symbtr_sourcetypes())
        for s in sfs:
            existing[s.file_type.slug] = s.get_absolute_url


    ret = {"add": uuid is None, "symbtr": symbtr, "url": url, "form": form,
            "symbtrfiles": symbtrfiles, "existingfiles": existing}
    return render(request, "dashboard/makam_symbtr.html", ret)

def _edit_artists_list(request, data):
    """ Generic view to display list of data.Artist """
    params = {"artists": data["artists"],
              "entityurl": data["entityurl"],
             }
    return render(request, data["template"], params)

def _edit_artist_desc(request, artist, entityurl):
    """ Generic view for editing a data.Artist """

    resp_msg = ""
    desc = None
    if artist.description is not None:
        desc = artist.description.description

    if request.method == 'POST':
        # Save description
        param_desc = request.POST.get("description", None)
        if param_desc is not None:
            # create the "Manual entry" data source if not created
            sn, created = data.models.SourceName.objects.get_or_create(name="Manual entry")
            source, created = data.models.Source.objects.get_or_create(source_name=sn, title="Manual entry", uri="")
            if created:
                source.save()
            if artist.description is None:
                description = data.models.Description(source=source, description=param_desc)
                description.save()
                artist.description = description
            else:
                artist.description.source = source
                artist.description.description = param_desc
                artist.description.save()
            artist.description_edited = True
            artist.save()
            resp_msg = "Description successfully edited"
            desc = param_desc

    params = {"artist": artist, "description": desc, "resp_msg": resp_msg, "entityurl": entityurl}
    return render(request, "dashboard/artist_edit.html", params)

def list_access_collections(request):
    """ List of data.Collection for edition """
    params = {"collections": data.models.Collection.objects.all()}
    return render(request, "dashboard/collections_list.html", params)

def edit_access_collections(request, uuid):
    message = ""
    collection = get_object_or_404(data.models.Collection, mbid=uuid)
    if request.method == 'POST':
        form = forms.AccessCollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            message = "The collection has been successfully edited"
    else:
        form = forms.AccessCollectionForm(instance=collection)
    params = {"form": form, "collection": collection, "message": message}
    return render(request, "dashboard/collections_edit.html", params)

def import_andalusian_elements(request):
    message=""
    if request.method == 'POST':
        form = forms.CsvAndalusianForm(request.POST, request.FILES)
        if form.is_valid():
            transliterator = ALA_LC_Transliterator()
            vocalizer=TashkeelClass()
            csv_file = form.cleaned_data['csv_file']
            reader = csv.reader(csv_file.read().splitlines())
            klass = None
            if form.cleaned_data['elem_type'] == 'tabs':
                klass = andalusian.models.Tab
            elif form.cleaned_data['elem_type'] == 'nawbas':
                klass = andalusian.models.Nawba
            elif form.cleaned_data['elem_type'] == 'forms':
                klass = andalusian.models.Form
            elif form.cleaned_data['elem_type'] == 'mizans':
                klass = andalusian.models.Mizan
            if klass:
                for row in reader:
                    elem, created = klass.objects.get_or_create(name = row[0].decode('utf8'))

                    voc = vocalizer.tashkeel(row[0].decode('utf8'))
                    tr = transliterator.do(voc.strip())
                    elem.transliterated_name = arabic_reshaper.reshape(tr)
                    elem.save()
                message = "The elements has been successfully loaded"
    else:
        form = forms.CsvAndalusianForm()
    params = {"form": form, "message": message}
    return render(request, "dashboard/load_csv.html", params)

def import_andalusian_catalog(request):
    message=""
    if request.method == 'POST':
        form = forms.CsvAndalusianCatalogForm(request.POST, request.FILES)
        if form.is_valid():
            transliterator = ALA_LC_Transliterator()
            vocalizer=TashkeelClass()
            omited = 0
            csv_file = form.cleaned_data['csv_file']
            reader = csv.reader(csv_file.read().splitlines())
            next(reader)
            for row in reader:

                genre = row[0]
                rec_mbid = row[11]
                nawba = row[14]
                tab = row[15]
                form = row[16]
                mizan = row[17]

                if rec_mbid:
                    section_start = row[18]
                    section_end = row[19]
                    genre, created = andalusian.models.Genre.objects.get_or_create(name = genre.decode('utf8'))
                    rec = andalusian.models.Recording.objects.get(mbid = rec_mbid)
                    sec, created = andalusian.models.Section.objects.get_or_create(recording=rec, start_time=section_start, end_time=section_end)
                    tab = andalusian.models.Tab.objects.get(name=tab.decode('utf8'))
                    form = andalusian.models.Form.objects.get(name=form.decode('utf8'))
                    nawba = andalusian.models.Nawba.objects.get(name=nawba.decode('utf8'))
                    mizan = andalusian.models.Mizan.objects.get(name=mizan.decode('utf8'))

                    voc = vocalizer.tashkeel(row[0].decode('utf8'))
                    tr = transliterator.do(voc.strip())
                    genre.transliterated_name = arabic_reshaper.reshape(tr)
                    genre.save()

                    voc = vocalizer.tashkeel(rec.title)
                    tr = transliterator.do(voc.strip())
                    rec.transliterated_title = arabic_reshaper.reshape(tr)
                    rec.genre = genre
                    rec.save()

                    sec.mizan = mizan
                    sec.tab = tab
                    sec.form = form
                    sec.nawba = nawba
                    sec.save()
                else:
                    omited += 1
            message = "The elements has been successfully loaded"
            if omited:
                message += "(%d rows omited)" % omited
    else:
        form = forms.CsvAndalusianCatalogForm()
    params = {"form": form, "message": message}
    return render(request, "dashboard/load_catalog_csv.html", params)



