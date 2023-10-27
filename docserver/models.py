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

import collections
import os

import django.utils.timezone
from django.conf import settings
from django.urls import reverse
from django.core.validators import RegexValidator
from django.db import models, connection
from django.template.defaultfilters import slugify

from docserver import exceptions


class Collection(models.Model):
    """A set of related documents"""

    class Meta:
        permissions = (('read_restricted', "Can read files in restricted collections"),)

    collectionid = models.UUIDField()
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    description = models.CharField(max_length=200)
    data = models.TextField(blank=True)

    root_directory = models.CharField(max_length=200)

    def __str__(self):
        desc = f"{self.name} ({self.slug})"
        if self.description:
            desc += f" - {self.description}"
        return desc

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Collection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("docserver-collection", args=[self.slug])


class DocumentManager(models.Manager):
    def get_by_external_id(self, external_id):
        return self.get_queryset().get(external_identifier=external_id)


class Document(models.Model):
    """An item in the collection.
    It has a known title and is part of a collection.
    It can have an option title and description
    """
    objects = DocumentManager()

    collections = models.ManyToManyField(Collection, related_name='documents')
    title = models.CharField(max_length=500)
    """If the file is known in a different database, the identifier
       for the item."""
    external_identifier = models.CharField(max_length=200, blank=True, null=True)

    def get_root_dir(self):
        root_directory = None
        for c in self.collections.all():
            if root_directory and root_directory != c.root_directory:
                raise exceptions.NoRootDirectoryException(
                    "If a document is in more than one collection they must have the same root_directory")
            root_directory = c.root_directory
        if not root_directory:
            raise exceptions.NoRootDirectoryException("This document is in no collection and so has no root directory")
        return root_directory

    def get_absolute_url(self):
        return reverse("ds-document-external", args=[self.external_identifier])

    def __str__(self):
        ret = u""
        if self.title:
            ret += f"{self.title}"
        if self.external_identifier:
            ret += f" ({self.external_identifier})"
        return ret

    def nestedderived(self):
        """Derived files to show on the dashboard """

        outputs = collections.defaultdict(list)
        for d in self.derivedfiles.all():
            outputs[d.module_version.module].append(d)
        for k, vs in outputs.items():
            versions = {}
            for v in vs:
                if v.module_version.version in versions:
                    versions[v.module_version.version].append(v)
                else:
                    versions[v.module_version.version] = [v]
            outputs[k] = versions
        outputs = dict(outputs)
        return outputs

    def derivedmap(self):
        """ Derived files for the API.
        returns {"slug": {"part": {"versions", [versions], "extension"...} ]}

        This makes an assumption that the number of parts and extension
        are the same for all versions. At the moment they are, but
        I'm not sure what to do if not
        """
        ret = collections.defaultdict(list)
        derived = self.derivedfiles.all()
        for d in derived:
            item = {"extension": d.extension, "version": d.module_version.version,
                    "outputname": d.outputname, "numparts": d.num_parts,
                    "mimetype": d.mimetype}
            ret[d.module_version.module.slug].append(item)
        newret = {}
        for k, v in ret.items():
            items = collections.defaultdict(list)
            for i in v:
                name = i['outputname']
                if name in items:
                    is_last_version = True
                    for curr in items[name]["versions"]:
                        is_last_version &= curr < i["version"]
                    if is_last_version:
                        items[name]["numparts"] = i["numparts"]
                    items[name]["versions"].append(i["version"])
                else:
                    items[name] = {"extension": i["extension"],
                                   "numparts": i["numparts"],
                                   "mimetype": i["mimetype"],
                                   "versions": [i["version"]]}

            newret[k] = items
        return newret

    def get_file(self, slug, subtype=None, part=None, version=None):
        try:
            sourcetype = SourceFileType.objects.get_by_slug(slug)
        except SourceFileType.DoesNotExist:
            sourcetype = None

        if sourcetype:
            files = self.sourcefiles.filter(file_type=sourcetype)
            if len(files) == 0:
                raise exceptions.NoFileException("Looks like a sourcefile, but I can't find one")
            else:
                return files[0]

        try:
            module = Module.objects.get(slug=slug)
        except Module.DoesNotExist:
            raise exceptions.NoFileException(f"Cannot find a module with type {slug}")
        moduleversions = module.versions
        if version:
            moduleversions = moduleversions.filter(version=version)
        else:
            moduleversions = moduleversions.order_by("-date_added")
        if len(moduleversions) == 0:
            raise exceptions.NoFileException("No known versions for this module")

        dfs = None
        for mv in moduleversions:
            # go through all the versions until we find a file of that version
            # If we have a more recent version, but only a derived file for an older
            # version, return the older version.
            dfs = self.derivedfiles.filter(module_version=mv).all()
            if subtype:
                dfs = dfs.filter(outputname=subtype)
            if dfs.count() > 0:
                # We found some files, break
                break
        if dfs.count() > 1:
            raise exceptions.TooManyFilesException(
                "Found more than 1 subtype for this module but you haven't specified what you want")
        elif dfs.count() == 1:
            # Double-check if subtypes match. This is to catch the case where we
            # have only one subtype for a type but we don't specify it in the
            # query. By 'luck' we will get the right subtype, but this doesn't
            # preclude the default subtype changing in a future version.
            # Explicit is better than implicit
            derived = dfs.get()
            if derived.outputname != subtype:
                raise exceptions.NoFileException(
                    f"This module has only one subtype which you must specify ({derived.outputname})")
            # Select the part.
            # If the file has many parts and ?part is not set then it's an error
            if part:
                try:
                    part = int(part)
                except ValueError:
                    raise exceptions.NoFileException("Invalid part")
                if part > derived.num_parts:
                    raise exceptions.NoFileException("Invalid part")

            if derived.num_parts == 0:
                raise exceptions.NoFileException("No parts on this file")
            elif derived.num_parts > 1 and not part:
                raise exceptions.TooManyFilesException("Found more than 1 part without part set")
            else:
                return derived
        else:
            # If no files, or none with this version
            msg = "No derived files with this type/subtype"
            if version:
                msg += " or version"
            raise exceptions.NoFileException(msg)


class FileTypeManager(models.Manager):
    def get_by_slug(self, slug):
        slug = slug.lower()
        return self.get_queryset().get(slug=slug)


class SourceFileType(models.Model):
    FILE_TYPE_CHOICES = (
        ('audio', 'Audio'),
        ('data', 'Data'),
    )
    objects = FileTypeManager()

    slug = models.SlugField(db_index=True, validators=[
        RegexValidator(regex="^[a-z0-9-]+$", message="Slug can only contain a-z 0-9 and -")])
    extension = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    mimetype = models.CharField(max_length=100)

    stype = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, blank=False, null=False)

    def __str__(self):
        return f"{self.name} ({self.slug})"

    def get_absolute_url(self):
        return reverse("docserver-filetype", args=[self.slug])


class SourceFile(models.Model):
    """An actual file. References a document"""

    """The document this file is part of"""
    document = models.ForeignKey(Document, related_name='sourcefiles', on_delete=models.CASCADE)
    """The filetype"""
    file_type = models.ForeignKey(SourceFileType, on_delete=models.CASCADE)
    """The relative path on disk to the file (to the collection root)"""
    path = models.CharField(max_length=500)
    size = models.IntegerField()

    @property
    def extension(self):
        return self.file_type.extension

    @property
    def slug(self):
        return self.file_type.slug

    def get_absolute_url(self, url_slug='ds-download-external', partnumber=None):
        # partnumber is ignored here, it is added so that the DerivedFile one works
        return reverse(
            url_slug,
            args=[self.document.external_identifier, self.file_type.slug])

    @property
    def fullpath(self):
        root_directory = self.document.get_root_dir()
        return os.path.join(root_directory, self.file_type.stype, self.path)

    @property
    def mimetype(self):
        return self.file_type.mimetype

    def __str__(self):
        return f"{self.document.title} ({self.file_type.name}, {self.path})"


class DerivedFile(models.Model):
    """A file which is the result of processing a SourceFile with an algorithm"""

    class Meta:
        unique_together = ("document", "module_version", "outputname")

    """The document this file is part of"""
    document = models.ForeignKey("Document", related_name='derivedfiles', on_delete=models.CASCADE)

    # A module could output more than 1 file. The combination of
    # module_version and (outputname/extension) refers to one
    # unique file output.
    module_version = models.ForeignKey("ModuleVersion", on_delete=models.CASCADE)
    outputname = models.CharField(max_length=50)
    extension = models.CharField(max_length=10)
    mimetype = models.CharField(max_length=100)
    computation_time = models.IntegerField(blank=True, null=True)

    # How many parts this DerivedFile is made up of
    num_parts = models.IntegerField()

    # The version of essentia and pycompmusic we used to compute this file
    essentia = models.ForeignKey("EssentiaVersion", blank=True, null=True, on_delete=models.CASCADE)
    pycompmusic = models.ForeignKey("PyCompmusicVersion", blank=True, null=True, on_delete=models.CASCADE)

    date = models.DateTimeField(default=django.utils.timezone.now)

    @property
    def versions(self):
        versions = self.module_version.module.versions.all()
        return [v.version for v in versions]

    def directory(self):
        root_directory = self.document.get_root_dir()
        recordingid = self.document.external_identifier
        version = self.module_version.version
        slug = self.module_version.module.slug

        recordingstub = str(recordingid)[:2]
        reldir = os.path.join(recordingstub, str(recordingid), slug, version)
        fdir = os.path.join(root_directory, settings.DERIVED_FOLDER, reldir)
        return fdir

    def full_path_for_part(self, partnumber):
        if not partnumber:
            raise exceptions.NoFileException("Invalid part")
        try:
            partnumber = int(partnumber)
        except ValueError:
            raise exceptions.NoFileException("Invalid part")
        if partnumber > self.num_parts:
            raise exceptions.NoFileException("partnumber is greater than number of parts")
        return os.path.join(self.directory(), self.filename_for_part(partnumber))

    def filename_for_part(self, partnumber):
        recordingid = self.document.external_identifier
        slug = self.module_version.module.slug
        version = self.module_version.version
        partslug = self.outputname
        extension = self.extension

        return f"{recordingid}-{slug}-{version}-{partslug}-{partnumber}.{extension}"

    def get_absolute_url(self, partnumber=None):
        url = reverse(
            "ds-download-external",
            args=[self.document.external_identifier, self.module_version.module.slug])
        v = self.module_version.version
        sub = self.outputname
        url = f"{url}?v={v}&subtype={sub}"
        if partnumber:
            try:
                partnumber = int(partnumber)
            except ValueError:
                raise exceptions.NoFileException("Invalid part")
            url = f"{url}&part={partnumber}"
        return url

    def __str__(self):
        return f"{self.document.title} ({self.module_version.module.slug}/{self.outputname})"


class CollectionPermission(models.Model):
    class Meta:
        permissions = (
            ("access_restricted_file", "Can see restricted source files"),
        )

    PERMISSIONS = (
        ('S', 'Staff-only'),
        ('R', 'Restricted'),
        ('U', 'Unrestricted')
    )

    permission = models.CharField(max_length=1, choices=PERMISSIONS, default='S')
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    source_type = models.ForeignKey(SourceFileType, on_delete=models.CASCADE)
    streamable = models.BooleanField(default=False)


# Essentia management stuff

class Worker(models.Model):
    NEW = "0"
    UPDATING = "1"
    UPDATED = "2"
    STATE_CHOICES = (
        (NEW, 'New'),
        (UPDATING, 'Updating'),
        (UPDATED, 'Updated')
    )

    hostname = models.CharField(max_length=200)
    essentia = models.ForeignKey("EssentiaVersion", blank=True, null=True, on_delete=models.CASCADE)
    pycompmusic = models.ForeignKey("PyCompmusicVersion", blank=True, null=True, on_delete=models.CASCADE)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default='0')

    def set_state_updating(self):
        self.state = self.UPDATING
        self.save()

    def set_state_updated(self):
        self.state = self.UPDATED
        self.save()

    def __str__(self):
        return f"{self.hostname} with Essentia {self.essentia} and Compmusic {self.pycompmusic}"


class PyCompmusicVersion(models.Model):
    sha1 = models.CharField(max_length=200)
    commit_date = models.DateTimeField(default=django.utils.timezone.now)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    @property
    def short(self):
        return self.sha1[:7]

    def get_absolute_url(self):
        return f"https://github.com/MTG/pycompmusic/tree/{self.sha1}"

    def short_link(self):
        return f"""<a href="{self.get_absolute_url()}">{self.short}</a>"""

    def __str__(self):
        return f"{self.sha1}"


class EssentiaVersion(models.Model):
    version = models.CharField(max_length=200)
    sha1 = models.CharField(max_length=200)
    commit_date = models.DateTimeField(default=django.utils.timezone.now)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    @property
    def short(self):
        return self.sha1[:7]

    def get_absolute_url(self):
        return f"https://github.com/MTG/essentia/tree/{self.sha1}"

    def short_link(self):
        return f"""<a href="{self.get_absolute_url()}">{self.short}</a>"""

    def __str__(self):
        return f"{self.version} ({self.sha1})"


class Module(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    depends = models.CharField(max_length=100, blank=True, null=True)
    module = models.CharField(max_length=200)
    source_type = models.ForeignKey(SourceFileType, on_delete=models.CASCADE)
    disabled = models.BooleanField(default=False)
    restricted = models.BooleanField(default=False)
    many_files = models.BooleanField(default=False)

    collections = models.ManyToManyField(Collection)

    def __str__(self):
        return f"{self.name} ({self.module})"

    def processed_files(self):
        latest = self.get_latest_version()
        if latest:
            return latest.processed_files()
        else:
            # If we don't have a version we probably can't show files yet
            return []

    def unprocessed_files(self):
        latest = self.get_latest_version()
        if latest:
            return latest.unprocessed_files()
        else:
            return []

    def latest_version_number(self):
        version = self.get_latest_version()
        if version:
            return version.version
        else:
            return "(none)"

    def get_latest_version(self):
        versions = self.versions.order_by("-date_added")
        if len(versions):
            return versions[0]
        else:
            return None

    def get_absolute_url(self):
        return reverse("docserver-module", args=[self.pk])


class ModuleVersion(models.Model):
    module = models.ForeignKey(Module, related_name="versions", on_delete=models.CASCADE)
    version = models.CharField(max_length=10)
    date_added = models.DateTimeField(default=django.utils.timezone.now)

    def is_latest(self):
        return self.module.get_latest_version() == self

    def processed_files(self, collection=None):
        if not collection:
            collections = self.module.collections.all()
        else:
            collections = [collection]
        if self.module.many_files:
            coll_ids = [c.collectionid for c in collections]
            qs = Document.objects.filter(external_identifier__in=coll_ids)
        else:
            qs = Document.objects.filter(
                collections__in=collections,
                sourcefiles__file_type=self.module.source_type)
        qs = qs.filter(derivedfiles__module_version=self)

        return qs.distinct()

    def unprocessed_files(self, collection=None):
        if not collection:
            collections = self.module.collections.all()
        else:
            collections = [collection]
        if self.module.many_files:
            total = len(collections) - len(self.processed_files(collection))
            return list(range(total))
        else:
            qs = Document.objects.filter(
                collections__in=collections,
                sourcefiles__file_type=self.module.source_type)
            qs = qs.exclude(derivedfiles__module_version=self)
            return qs.distinct()

    def processed_files_count(self):
        q = '''SELECT count(distinct document_id) FROM "docserver_derivedfile" WHERE module_version_id = %d''' % (
        self.id)
        cursor = connection.cursor()
        cursor.execute(q)
        row = cursor.fetchone()
        return row[0]

    def unprocessed_files_count(self):
        collections = self.module.collections.all()
        if len(collections) == 0:
            return 0
        coll_ids = [str(c.id) for c in collections]
        q = '''
SELECT COUNT(DISTINCT "docserver_document"."id")
FROM "docserver_document"
INNER JOIN "docserver_sourcefile" ON ( "docserver_document"."id" = "docserver_sourcefile"."document_id" )
INNER JOIN "docserver_document_collections" ON ( "docserver_document"."id" = "docserver_document_collections"."document_id" )
WHERE ("docserver_sourcefile"."file_type_id" = %d
AND "docserver_document_collections"."collection_id" IN (%s)
AND NOT ("docserver_document"."id" IN (
    SELECT U1."document_id" AS Col1 FROM "docserver_derivedfile" U1 WHERE U1."module_version_id" = %d
)))''' % (self.module.source_type.id, ', '.join(coll_ids), self.id)
        cursor = connection.cursor()
        cursor.execute(q)
        row = cursor.fetchone()
        return row[0]

    def __str__(self):
        return f"v{self.version} for {self.module}"


class DocumentLogMessage(models.Model):
    """ A log message about a document. Normally the log message refers to ModuleVersion
    processing a specific SourceFile, but these can be blank """

    class Meta:
        ordering = ['-datetime']

    document = models.ForeignKey(Document, related_name="logs", on_delete=models.CASCADE)
    moduleversion = models.ForeignKey(ModuleVersion, blank=True, null=True, on_delete=models.CASCADE)
    sourcefile = models.ForeignKey(SourceFile, blank=True, null=True, on_delete=models.CASCADE)
    level = models.CharField(max_length=20)
    message = models.TextField()
    datetime = models.DateTimeField(default=django.utils.timezone.now)

    def is_exception(self):
        return "Traceback (most recent call last)" in self.message

    def __str__(self):
        return f"{self.datetime}: {self.message}"
