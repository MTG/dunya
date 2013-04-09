from fabric.api import *
import os

def up(port="8001"):
    local("python manage.py runserver 0.0.0.0:%s"%port)

def reset():
    local("python manage.py syncdb --noinput")

def dumpfixture(modname):
    with hide('running', 'status'):
        redir = "%s/fixtures/initial_data.json" % modname
        if modname == "data":
            local("python manage.py dumpdata data data.SourceName --indent=4 > %s" % redir)
        elif modname == "carnatic": 
            local("python manage.py dumpdata carnatic carnatic.Instrument carnatic.Taala carnatic.Raaga carnatic.GeographicRegion --indent=4 > %s" % redir)

def dumpdata(fname="dunya_data.json"):
    with hide('running', 'status'):
        modules = ["browse", "carnatic", "data", "docserver", "social"]
        local("python manage.py dumpdata --indent=4 %s > %s" % (" ".join(modules), fname))
        print "dumped data to %s" % fname

def loaddata(fname="dunya_data.json"):
    print "Loading data from %s" % fname
    if os.path.exists(fname):
        local("python manage.py loaddata %s" % fname)
    else:
        print " (missing!)"

def test():
    local("python manage.py test browser")
