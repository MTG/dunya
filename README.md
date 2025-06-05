Dunya
=====

Introduction
------------
Dunya is a prototype being developed in the context of CompMusic, a
research project that studies several world music traditions from the
point of view of the information technologies, with the aim to
facilitate the cataloging and discovery of music recordings within
large repositories. For more information: http://compmusic.upf.edu

License
=======
Dunya is Copyright 2013-2018 Music Technology Group - Universitat Pompeu Fabra

Dunya is released under the terms of the GNU Affero General Public
License (v3 or later). See the COPYING file for more information.

If you would prefer to get a (non FOSS) commercial license, please
contact us at mtg@upf.edu

Installation
============
First, create directories for pycompmusic (cloned from https://github.com/MTG/pycompmusic.git) and data (empty folder) somewhere outside the dunya folder.

Then, in the dunya directory, set the relevant environment variables to the absolute locations of these folders.

    cp .env.in .env

Insert the actual absolute paths in .env

Using docker, run

    docker compose build

to build the relevant packages, and then run

    docker compose up

to start it.

Setup
-----

Perform a database migration, and load fixture data

    docker compose run --rm web python3 manage.py migrate

    docker compose run --rm web python3 manage.py loaddata carnatic_form.json carnatic_raaga.json carnatic_instrument.json carnatic_taala.json data_initial_data.json docserver_groups.json docserver_sourcefiletype.json sites.json hindustani_form.json hindustani_laya.json hindustani_taal.json hindustani_instrument.json hindustani_raag.json makam_form.json makam_instrument.json makam_makam.json makam_usul.json jingju_roletype.json jingju_instrument.json jingju_shengqiangbanshi.json


Javascript
-----
Install npm modules

    docker compose run --rm --user `id -u`:`id -g` -e HOME=/tmp web npm install

Build required js packages

    docker compose run --rm --user `id -u`:`id -g` web npm run build


Stylesheets
-----
Compile less stylesheets

    docker compose run --rm --user `id -u`:`id -g` web sh build-less.sh


Updating Fixtures
=================

Some data in Dunya should only rarely change (e.g., Raaga, Taala, Form, Location, Language lists).
We store this data in _fixtures,_ and it is automatically loaded when you create a new database.
Fixure files are in `fixtures/initial_data.json` in the app (e.g., `data` and `carnatic`).

If you make a new fixture table, you can easily import data into it by creating a CSV file with
the data in the first column and running

    python tools/import_csv.py -t <fixturename> <csvfile>

You'll need to edit `import_csv.py` to tell it about your table.
You should then dump the fixtures to file and commit them for other people to use
(you'll need to edit the `dumpfixture` method in `fabfile.py` to tell it about the
new fixture, too.

    fab dumpfixture:carnatic


Development
===========
To clear the database you can remove the postgres volume:

    docker compose down
    docker volume rm dunya_dbvolume

Server configuration
====================

Find an nginx configuration file in the `admin/` directory.


Workers
=======

Dunya must also be installed on worker machines to run remote processes. This machine
will need access to the main database, configured in `local_settings.py`

Essentia should be installed into the virtual environment, `/srv/dunya/env`. The
whole dunya directory should be owned by a user that has write permission to the
directory. Celery should run as this user too.

You need to make sure that this user can connect to github via ssh. Either log in as the
use and run `ssh github.com`, or use https.

The celery configuration should have a queue and hostname configured that are the
same (`-Q` and `-n`). These settings are needed for remote control of a single worker.
The machines must also listen on the standard `celery` queue for all other work.

One machine must listen on the `import` queue. This is used for processes that run from
the dashboard.


Email
======

Emails are sent via gmail. We use the google API instead of SMTP because it's faster to send emails.
Because we send email only via one account, we manually set up the credentials
using the guide at https://developers.google.com/gmail/api/quickstart/python


Sign into gmail with the alastair.porter@upf.edu account and go to
https://console.cloud.google.com/projectcreate

There is a project called "dunya-email"
Enable the gmail API for this project, from https://console.cloud.google.com/apis/library?project=dunya-email

Configure the OAuth consent screen
User type: Internal
App Name: Dunya
User support email: alastair.porter@upf.edu
Application homepage: https://dunya.upf.edu
Authorized domains: upf.edu
Developer contact email: alastair.porter@upf.edu

go to Menu > APIs & Services > Credentials
Create credentials > OAuth client ID
Application type: Desktop app
Name: Dunya
Download the credentials file
