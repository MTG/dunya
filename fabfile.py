from __future__ import print_function

from fabric.api import local, hide
import os


def test(module=None, keepdb=True):
    command = "python manage.py test --settings=dunya.test_settings --noinput"
    if keepdb:
        command += " --keepdb"
    if module:
        command += f" {module}"
    if keepdb:
        print("Keeping DB (if available), run cleantest to recreate schema")
    local(command)


def cleantest(module=None):
    test(module, False)


def dumpfixture(modname):
    redir_base = "%s/fixtures/%s_%%s.json" % (modname, modname)
    if modname == "data":
        redir = redir_base % "initial_data"
        local(f"python manage.py dumpdata data.SourceName --indent=4 > {redir}")
        return
    elif modname == "carnatic":
        tablemap = {"instrument": ["Instrument", "InstrumentAlias"],
                    "taala": ["Taala", "TaalaAlias"],
                    "raaga": ["Raaga", "RaagaAlias"],
                    "form": ["Form", "FormAlias"]}
    elif modname == "hindustani":
        tablemap = {"instrument": ["Instrument"],
                    "taal": ["Taal", "TaalAlias"],
                    "raag": ["Raag", "RaagAlias"],
                    "form": ["Form", "FormAlias"],
                    "laya": ["Laya", "LayaAlias"]}
    elif modname == "makam":
        tablemap = {"instrument": ["Instrument"],
                    "makam": ["Makam", "MakamAlias"],
                    "form": ["Form", "FormAlias"],
                    "usul": ["Usul", "UsulAlias"]}
    for filename, tables in tablemap.items():
        modellist = " ".join([f"{modname}.{t}[:]" for t in tables])
        redir = redir_base % filename
        local(f"python manage.py makefixture {modellist} --indent=4 > {redir}")


def dumpdata(fname="dunya_data.json"):
    with hide('running', 'status'):
        modules = ["carnatic", "data", "docserver", "account", "auth", "dashboard"]
        local(f"python manage.py dumpdata --indent=4 {' '.join(modules)} > {fname}")
        print(f"dumped data to {fname}")


def loaddata(fname="dunya_data.json"):
    print(f"Loading data from {fname}")
    if os.path.exists(fname):
        local(f"python manage.py loaddata {fname}")
    else:
        print(" (missing!)")
