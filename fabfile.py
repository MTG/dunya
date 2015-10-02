from fabric.api import local, settings, env, roles, run, cd, hide, shell_env
import os

env.roledefs["web"] = ["sitar.s.upf.edu"]
env.roledefs["workers"] = ["itri.s.upf.edu", "devaraya.s.upf.edu", "amirkhusro.s.upf.edu", "kora.s.upf.edu", "guqin.s.upf.edu", "ziryab.s.upf.edu"]
env.use_ssh_config = True
env.forward_agent = True

def up(port="8001"):
    local("python manage.py runserver 0.0.0.0:%s"%port)

def celery():
    local("celery worker --app=dunya -l info")

def test(module=None, keepdb=True):
    command = "python manage.py test --settings=dunya.test_settings --noinput"
    if keepdb:
        command += " --keepdb"
    if module:
        command += " %s" % module
    if keepdb:
        print "Keeping DB (if available), run cleantest to recreate schema"
    local(command)

def cleantest(module=None):
    test(module, False)

@roles("workers")
def pipinstall():
    """Install new dependencies added to requirements"""
    env.user = "mtg_dunya"
    with cd("/srv/dunya"):
        run("env/bin/pip install -r requirements")

    run("sudo supervisorctl restart dunya")


@roles("web")
def updateweb():
    """Update the webserver"""
    env.user = "mtg_dunya"
    with cd("/srv/dunya"):
        run("git pull", pty=False)
        # compile and compress less
        # compress javascript
        run("env/bin/python manage.py collectstatic --noinput")

        run("env/bin/node env/bin/lessc carnatic/static/carnatic/css/main.less static/carnatic/css/main.css")
        run("env/bin/node env/bin/lessc carnatic/static/carnatic/css/browse.less static/carnatic/css/browse.css")
        run("env/bin/node env/bin/lessc carnatic/static/carnatic/css/recording.less static/carnatic/css/recording.css")
        run("env/bin/node env/bin/lessc carnatic/static/carnatic/css/pages.less static/carnatic/css/pages.css")
        run("env/bin/node env/bin/lessc carnatic/static/carnatic/css/presentation.less static/carnatic/css/presentation.css")

    with cd("/srv/dunya/env/src/pycompmusic"):
        run("git pull", pty=False)

    run("sudo supervisorctl restart dunya")

@roles("workers")
@roles("web")
def essentia(branch=None):
    """Update essentia on all workers"""
    with cd("/srv/essentia"):
        run("git pull", pty=False)
        run("./waf -j4")
        run("./waf install")

@roles("workers")
def updatecelery():
    env.user = "mtg_dunya"
    """Update the code for celery on all workers and restart"""
    with cd("/srv/dunya"):
        run("git pull", pty=False)
    with cd("/srv/dunya/env/src/pycompmusic"):
        run("git pull", pty=False)
    run("sudo supervisorctl restart dunyacelery")

def setupdb():
    """ Run this when you are setting up a new installation
        or have deleted your database
    """
    local("python manage.py migrate")
    local("python manage.py mkdunyadata")

def updatedb():
    """ Run this when someone has committed some changes to the
        database migration scripts
    """
    local("python manage.py migrate")

def dumpfixture(modname):
    redir_base = "%s/fixtures/%s_%%s.json" % (modname, modname)
    if modname == "data":
        redir = redir_base % "initial_data"
        local("python manage.py dumpdata data.SourceName --indent=4 > %s" % redir)
    elif modname == "carnatic":
        tablemap = {"instrument": ["Instrument", "InstrumentAlias"],
                  "taala": ["Taala", "TaalaAlias"],
                  "raaga": ["Raaga", "RaagaAlias"],
                  "form": ["Form", "FormAlias"],
                  "misc": ["Language", "MusicalSchool"]}
    elif modname == "hindustani":
        tablemap = {"instrument": ["Instrument"],
                  "taal": ["Taal", "TaalAlias"],
                  "raag": ["Raag", "RaagAlias"],
                  "form": ["Form", "FormAlias"],
                  "laya": ["Laya", "LayaAlias"],
                  "section": ["Section", "SectionAlias"]}
    elif modname == "makam":
        tablemap = {"instrument": ["Instrument"],
                    "makam": ["Makam", "MakamAlias"],
                    "form": ["Form", "FormAlias"],
                    "usul": ["Usul", "UsulAlias"]}
    for filename, tables in tablemap.items():
        modellist = " ".join(["%s.%s[:]" % (modname, t) for t in tables])
        redir = redir_base % filename
        local("python manage.py makefixture %s --indent=4 > %s" % (modellist, redir))

def dumpdata(fname="dunya_data.json"):
    with hide('running', 'status'):
        modules = ["carnatic", "data", "docserver", "account", "auth", "dashboard"]
        local("python manage.py dumpdata --indent=4 %s > %s" % (" ".join(modules), fname))
        print "dumped data to %s" % fname

def loaddata(fname="dunya_data.json"):
    print "Loading data from %s" % fname
    if os.path.exists(fname):
        local("python manage.py loaddata %s" % fname)
    else:
        print " (missing!)"
