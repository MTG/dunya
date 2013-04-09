The CompMusic Browser
=====================


Installation
============

    apt-get install postgresql python-dev python-virtualenv
    virtualenv --no-site-packages env
    source env/bin/activate
    pip install --upgrade distribute
    pip install -r requirements

Copy the file `dunya/local_settings.py.dist` to `dunya/local_settings.py` and edit it
to point to your database. It does not matter if you use postgres, mysql, or sqlite.

To add tables to the database run

    fab setupdb

Running
=======

To run the server:

    source env/bin/activate
    fab up

When you upgrade and there are database changes, you can run this to migrate them

    fab updatedb

To make a complete dump of the database to a file called `dunya_data.json` or to
load it again, run

    fab dumpdata
    fab loaddata

Updating Fixtures
=================

Some data in Dunya should only rarely change (e.g., Raaga, Taala, Form, Location, Language lists).
We store this in _fixtures,_ and it is automatically loaded when you create a new database.
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

In the data module there are 5 abstract classes:

 * Artist
 * Composer
 * Work
 * Concert
 * Recording

These classes store fields that are common to all cultures.

They also store lookup properties that are common over all styles, e.g.,
`concert.performers()`

Each style has replicas of these classes that can inherit from these
abstract classes.

The abstract classes also provide the `get_absolute_url()` method, to be used
when referring to an object.

both `get_absolute_url` and property lookups require data (class names, url fragments) that
are common to the specific culture. Because of this, you need to create a StyleBase class
which implements two methods. Here is an example:

    class CarnaticBase(object):
        def get_style(self):
            return "carnatic"
        def get_object_map(self):
            return {"performance": InstrumentPerformance,
                    "concert": Concert
            }

You need an object map for each of the abstract classes.

A specific culture has a concrete class inheriting from the base class ''first'' and
then the abstract data class

    class Concert(CarnaticBase, data.models.BaseConcert):

Any fields that are specific to this culture can be added to this specific class.

Templates
=========

To get the application chrome, add this to the top of the template

    {% extends "browse/base.html" %}

and put the contents of the template inside

    {% block wrap %}
    ...
    {% endblock %}

Template files should be saved in `modulename/templates/modulename/templatename.html` and can be
refered to in a view as `modulename/templatename.html`

Template fragments
==================

Commonly used parts of code are added to template fragments.

We need a better description about how to name these and what the arguments should be.

Inline links
============
When linking to an entity, never construct a link manually. Instead, make sure the template contains

    {% load extras %}

and use the provided `{% inline_x thex %}` methods. These will automatically create a link and
the best form of the objects name.
