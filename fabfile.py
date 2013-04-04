from fabric.api import *

def up(port="8001"):
    local("python manage.py runserver 0.0.0.0:%s"%port)

def reset():
    local("python manage.py syncdb --noinput")

def dump():
    with hide('running', 'status'):
        local("python manage.py dumpdata data data.SourceName --indent=4")
        local("python manage.py dumpdata carnatic carnatic.Instrument carnatic.Taala carnatic.Raaga --indent=4")

def test():
    local("python manage.py test browser")
