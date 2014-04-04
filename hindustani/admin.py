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

from hindustani import models
from django.contrib import admin

class ArtistAliasInline(admin.TabularInline):
    model = models.ArtistAlias
    extra = 1

class ComposerAliasInline(admin.TabularInline):
    model = models.ComposerAlias
    extra = 1

class ReleaseRecordingInline(admin.TabularInline):
    model = models.ReleaseRecording
    extra = 1

class WorkTimeInline(admin.TabularInline):
    model = models.WorkTime
    extra = 1

class RecordingRaagInline(admin.TabularInline):
    model = models.RecordingRaag
    extra = 1

class RecordingTaalInline(admin.TabularInline):
    model = models.RecordingTaal
    extra = 1

class RecordingSectionInline(admin.TabularInline):
    model = models.RecordingSection
    extra = 1

class RecordingFormInline(admin.TabularInline):
    model = models.RecordingForm
    extra = 1

class ArtistAdmin(admin.ModelAdmin):
    inlines = (ArtistAliasInline, )

class ComposerAdmin(admin.ModelAdmin):
    inlines = (ComposerAliasInline, )

class ReleaseAdmin(admin.ModelAdmin):
    inlines = (RecordingRaagInline, RecordingTaalInline, RecordingFormInline, RecordingSectionInline, ReleaseRecordingInline, WorkTimeInline)

admin.site.register(models.Instrument)
admin.site.register(models.InstrumentPerformance)
admin.site.register(models.Artist, ArtistAdmin)

admin.site.register(models.Release, ReleaseAdmin)
admin.site.register(models.Section)
admin.site.register(models.Raag)
admin.site.register(models.Taal)
admin.site.register(models.Laay)
admin.site.register(models.Form)
admin.site.register(models.Work)
admin.site.register(models.Recording)

admin.site.register(models.Composer, ComposerAdmin)

