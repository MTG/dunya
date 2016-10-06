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

from makam import models
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

class RecordingWorkInline(admin.TabularInline):
    model = models.RecordingWork
    extra = 1

class InstrumentPerformanceInline(admin.TabularInline):
    model = models.InstrumentPerformance
    extra = 1

class ArtistAdmin(admin.ModelAdmin):
    inlines = (ArtistAliasInline, )
    exclude = ('images', 'description')

class InstrumentAdmin(admin.ModelAdmin):
    exclude = ('images', 'description')

class ComposerAdmin(admin.ModelAdmin):
    inlines = (ComposerAliasInline, )
    exclude = ('images', 'description')

class ReleaseAdmin(admin.ModelAdmin):
    exclude = ('images', )

class RecordingAdmin(admin.ModelAdmin):
    inlines = (RecordingWorkInline, InstrumentPerformanceInline)
    exclude = ('images', )

class WorkAdmin(admin.ModelAdmin):
    exclude = ('images', )

admin.site.register(models.Artist, ArtistAdmin)
admin.site.register(models.Composer, ComposerAdmin)
admin.site.register(models.Instrument, InstrumentAdmin)
admin.site.register(models.Makam)
admin.site.register(models.Form)
admin.site.register(models.Usul)
admin.site.register(models.SymbTr)
admin.site.register(models.Work, WorkAdmin)
admin.site.register(models.Release, ReleaseAdmin)
admin.site.register(models.Recording, RecordingAdmin)
