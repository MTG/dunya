from docserver import models
from django.contrib import admin

admin.site.register(models.Collection)
admin.site.register(models.Document)
admin.site.register(models.SourceFileType)
admin.site.register(models.SourceFile)
admin.site.register(models.DerivedFile)
admin.site.register(models.EssentiaVersion)
admin.site.register(models.Module)
admin.site.register(models.ModuleVersion)

