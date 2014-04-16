from fabric.api import local, settings, env, roles, run, cd
import os

env.roledefs["web"] = ["sitar.s.upf.edu"]
env.roledefs["workers"] = ["itri.s.upf.edu", "devaraya.s.upf.edu", "amirkhusro.s.upf.edu", "kora.s.upf.edu", "guqin.s.upf.edu", "ziryab.s.upf.edu"]
env.use_ssh_config = True
env.forward_agent = True

def up(port="8001"):
    local("python manage.py runserver 0.0.0.0:%s"%port)

def celery():
    local("celery worker --app=dunya -l info")

def test(module=None):
    command = "python manage.py test --settings=dunya.test_settings"
    if module:
        command += " %s" % module
    local(command)

@roles("web")
def updateweb():
    """Update the webserver"""
    with cd("/srv/dunya"):
        run("git pull")
        # compile and compress less
        # compress javascript
        run("env/bin/python manage.py collectstatic --noinput")
        less()
    with cd("/srv/dunya/env/src/pycompmusic"):
        run("git pull")
    run("sudo supervisorctl restart dunya")

@roles("workers")
@roles("web")
def essentia(branch=None):
    """Update essentia on all workers"""
    with cd("/srv/essentia"):
        run("git pull")
        run("./waf -j4")
        run("sudo ./waf install")

@roles("workers")
def updatecelery():
    """Update the code for celery on all workers and restart"""
    with cd("/srv/dunya"):
        run("git pull")
    with cd("/srv/dunya/env/src/pycompmusic"):
        run("git pull")
    run("sudo supervisorctl restart dunyacelery")

def less():
    """Compile less into static css"""
    local("lessc carnatic/static/carnatic/css/main.less static/carnatic/css/main.css")
    local("lessc carnatic/static/carnatic/css/browse.less static/carnatic/css/browse.css")
    local("lessc carnatic/static/carnatic/css/recording.less static/carnatic/css/recording.css")
    local("lessc carnatic/static/carnatic/css/pages.less static/carnatic/css/pages.css")
    local("lessc carnatic/static/carnatic/css/presentation.less static/carnatic/css/presentation.css")

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
    local("python manage.py migrate")

def dumpfixture(modname):
    redir = "%s/fixtures/initial_data.json" % modname
    if modname == "data":
        local("python manage.py dumpdata data.SourceName --indent=4 > %s" % redir)
    elif modname == "carnatic":
        tables = ["Instrument", "InstrumentAlias", "Taala", "TaalaAlias", "Raaga", "RaagaAlias", "GeographicRegion", "Form", "FormAlias", "Language", "MusicalSchool"]
        modellist = " ".join(["carnatic.%s[:]" % t for t in tables])
        local("python manage.py makefixture %s --indent=4 > %s" % (modellist, redir))
    elif modname == "hindustani":
        tables = ["Instrument", "Taal", "TaalAlias", "Raag", "RaagAlias", "Laay", "LaayAlias", "Form", "FormAlias", "Section", "SectionAlias"]
        modellist = " ".join(["hindustani.%s[:]" % t for t in tables])
        local("python manage.py makefixture %s --indent=4 > %s" % (modellist, redir))
    elif modname == "makam":
        tables = ["Instrument", "Makam", "Form", "Usul"]
        modellist = " ".join(["makam.%s[:]" % t for t in tables])
        local("python manage.py makefixture %s --indent=4 > %s" % (modellist, redir))

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
