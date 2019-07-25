from django.contrib import admin

from andalusian import models


class OrchestraAliasInline(admin.TabularInline):
    model = models.OrchestraAlias
    extra = 1


class OrchestraAdmin(admin.ModelAdmin):
    inlines = (OrchestraAliasInline,)


class TabAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class NawbaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class MizanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class FormAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(models.Orchestra, OrchestraAdmin)
admin.site.register(models.Artist)
admin.site.register(models.AlbumRecording)
admin.site.register(models.Album)
admin.site.register(models.Work)
admin.site.register(models.Genre)
admin.site.register(models.RecordingWork)
admin.site.register(models.Recording)
admin.site.register(models.Instrument)
admin.site.register(models.OrchestraPerformer)
admin.site.register(models.Tab, TabAdmin)
admin.site.register(models.Nawba, NawbaAdmin)
admin.site.register(models.Mizan, MizanAdmin)
admin.site.register(models.Form, FormAdmin)
admin.site.register(models.Section)
admin.site.register(models.Sanaa)
admin.site.register(models.PoemType)
admin.site.register(models.Poem)