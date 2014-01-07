from fabric.api import *
import os

def up(port="8001"):
    local("python manage.py runserver 0.0.0.0:%s"%port)

def celery():
    local("celery worker --app=dunya -l info")

def less():
    local("lessc carnatic/static/carnatic/css/main.less --source-map-map-inline carnatic/static/carnatic/css/main.css")

def setupdb():
    """ Run this when you are setting up a new installation
        or have deleted your database
    """
    local("python manage.py syncdb --noinput")
    local("python manage.py migrate")
    local("python manage.py mkdunyadata")
    local("python manage.py mkfiletypes")

def updatedb():
    """ Run this when someone has committed some changes to the
        database migration scripts
    """
    local("python manage.py migrate data")
    local("python manage.py migrate carnatic")
    local("python manage.py migrate dashboard")
    local("python manage.py migrate docserver")
    local("python manage.py migrate social")

def migratedb():
    """ Run this if you make some changes to the models """
    with settings(warn_only=True):
        local("python manage.py schemamigration data --auto")
    with settings(warn_only=True):
        local("python manage.py schemamigration carnatic --auto")
    with settings(warn_only=True):
        local("python manage.py schemamigration dashboard --auto")
    with settings(warn_only=True):
        local("python manage.py schemamigration docserver --auto")
    with settings(warn_only=True):
        local("python manage.py schemamigration social --auto")

def initialdb(modulename):
    """ Use this to tell south to manage a new django app """
    local("python manage.py schemamigration %s --initial" % modulename)

def dumpfixture(modname):
    redir = "%s/fixtures/initial_data.json" % modname
    if modname == "data":
        local("python manage.py dumpdata data.SourceName --indent=4 > %s" % redir)
    elif modname == "carnatic":
        tables = ["Instrument", "InstrumentAlias", "Taala", "TaalaAlias", "Raaga", "RaagaAlias", "GeographicRegion", "Form", "Language", "MusicalSchool"]
        modellist = " ".join(["carnatic.%s" % t for t in tables])
        local("python manage.py dumpdata %s --indent=4 > %s" % (modellist, redir))

def dumpdata(fname="dunya_data.json"):
    with hide('running', 'status'):
        modules = ["carnatic", "data", "docserver", "social", "comments", "auth", "dashboard"]
        local("python manage.py dumpdata --indent=4 %s > %s" % (" ".join(modules), fname))
        print "dumped data to %s" % fname

def loaddata(fname="dunya_data.json"):
    print "Loading data from %s" % fname
    if os.path.exists(fname):
        local("python manage.py loaddata %s" % fname)
    else:
        print " (missing!)"
