import importlib

from docserver import models

def get_latest_module_version():
    modules = models.Module.objects.all()
    for m in modules:
        clsname = m.path
        mod, clsname = clsname.rsplit(".", 1)
        package = importlib.import_module(mod)
        cls = getattr(package, clsname)
        instance = cls()
        version = instance.__version__
        v = "%s" % version

        versions = m.moduleversion_set.all()
        if len(versions):
            versions = sorted(versions, reverse=True)
            last_version = versions[0]
            if v > last_version:
                create = True
        else:
            create = True
        if create:
            models.ModuleVersion.objects.create(module=m, version=v)

