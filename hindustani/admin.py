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

from django.contrib import admin

from hindustani import models


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


class RecordingPerformanceInline(admin.TabularInline):
    model = models.InstrumentPerformance
    extra = 1


class RecordingRaagInline(admin.TabularInline):
    model = models.RecordingRaag
    extra = 1


class RecordingLayaInline(admin.TabularInline):
    model = models.RecordingLaya
    extra = 1


class RecordingTaalInline(admin.TabularInline):
    model = models.RecordingTaal
    extra = 1


class RecordingFormInline(admin.TabularInline):
    model = models.RecordingForm
    extra = 1


class ArtistAdmin(admin.ModelAdmin):
    inlines = (ArtistAliasInline,)
    exclude = ('image', 'description')


class ComposerAdmin(admin.ModelAdmin):
    inlines = (ComposerAliasInline,)
    exclude = ('image', 'description')


class RecordingAdmin(admin.ModelAdmin):
    inlines = (RecordingRaagInline, RecordingTaalInline, RecordingLayaInline, RecordingFormInline, WorkTimeInline,
               RecordingPerformanceInline)


class ReleaseAdmin(admin.ModelAdmin):
    inlines = (ReleaseRecordingInline,)


class RaagAliasInline(admin.TabularInline):
    model = models.RaagAlias
    extra = 1


class RaagAdmin(admin.ModelAdmin):
    inlines = (RaagAliasInline,)
    exclude = ('image',)


class TaalAliasInline(admin.TabularInline):
    model = models.TaalAlias
    extra = 1


class TaalAdmin(admin.ModelAdmin):
    inlines = (TaalAliasInline,)
    exclude = ('image',)


class LayaAliasInline(admin.TabularInline):
    model = models.LayaAlias
    extra = 1


class LayaAdmin(admin.ModelAdmin):
    inlines = (LayaAliasInline,)


class FormAliasInline(admin.TabularInline):
    model = models.FormAlias
    extra = 1


class FormAdmin(admin.ModelAdmin):
    inlines = (FormAliasInline,)


admin.site.register(models.Instrument)
admin.site.register(models.InstrumentPerformance)
admin.site.register(models.Artist, ArtistAdmin)
admin.site.register(models.Release, ReleaseAdmin)
admin.site.register(models.Raag, RaagAdmin)
admin.site.register(models.Taal, TaalAdmin)
admin.site.register(models.Laya, LayaAdmin)
admin.site.register(models.Form, FormAdmin)
admin.site.register(models.Work)
admin.site.register(models.Recording, RecordingAdmin)
admin.site.register(models.Composer, ComposerAdmin)
