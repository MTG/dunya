from docserver import models
from django.contrib import admin

admin.site.register(models.Collection)
admin.site.register(models.Document)
admin.site.register(models.SourceFileType)
admin.site.register(models.SourceFile)
admin.site.register(models.DerivedFileType)
admin.site.register(models.DerivedFile)
admin.site.register(models.EssentiaVersion)
admin.site.register(models.WorkerMachine)
admin.site.register(models.WorkerMachineEssentiaVersion)
admin.site.register(models.Module)
admin.site.register(models.ModuleVersion)
admin.site.register(models.WorkerMachineModuleVersion)
admin.site.register(models.RunResult)
