# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/


import imp
import importlib
import inspect
import json
import os
import logging
from django.core.management.base import BaseCommand
import numpy as np

import compmusic

logger = logging.getLogger(__name__)

def _get_module_by_path(modulepath):
    mod, clsname = modulepath.rsplit(".", 1)
    try:
        package = importlib.import_module(mod)
        cls = getattr(package, clsname)
        return cls
    except ImportError:
        logger.warn("Cannot import the module: %s" % mod)
        logger.warn("Try it in a terminal and see what the error is")


def _get_module_by_slug(slug):
    # Get all files in the module
    fname, dirname, desc = imp.find_module("extractors", compmusic.__path__)
    modules = set(["compmusic.extractors.%s" % os.path.splitext(module)[0]
                   for module in os.listdir(dirname) if module.endswith(".py")])

    unloaded = []
    matching = []
    for m in modules:
        try:
            loaded = importlib.import_module(m)
            for name, mod in inspect.getmembers(loaded, inspect.isclass):
                if issubclass(mod, extractors.ExtractorModule) and name != "ExtractorModule":
                    if mod._slug == slug:
                        matching.append(mod)
        except ImportError:
            unloaded.append(m)

    if unloaded:
        logger.warn(
            "Failed to load these modules due to an import error, check that you have all their dependencies installed")
        for u in unloaded:
            logger.warn(u)

    if len(matching) > 1:
        logger.warn("Found more than one module with the same slug. Slugs must be unique")
        logger.warn("For slug: %s" % slug)
        for m in matching:
            logger.warn("  %s" % m)
    elif len(matching) == 1:
        return matching[0]
    else:
        logger.warn("Cannot find a module with the slug: %s" % slug)
        logger.warn("Check that you have spelt it correctly")
        if unloaded:
            logger.warn("or that the module it is in can be loaded (is it in one of the above failed modules?)")
        return None

def load_module(modulepath):
    if "." in modulepath:
        # it's an exact path
        module = _get_module_by_path(modulepath)
    else:
        # it's a slug, search for it.
        module = _get_module_by_slug(modulepath)
    if module:
        return module()
    else:
        return None


class NumPyArangeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # or map(int, obj)
        return json.JSONEncoder.default(self, obj)

def save_data(module, data):
    modulemeta = module._output
    mbid = module.musicbrainz_id
    for key, d in data.items():
        ext = modulemeta[key]["extension"]
        if modulemeta[key].get("parts", False) is False:
            d = [d]
        for i in range(len(d)):
            fname = "%s-%s-%s.%s" % (mbid, key, i, ext)
            print("Writing output for type %s to %s" % (key, fname))
            if modulemeta[key]["mimetype"] == "application/json":
                output = json.dumps(d[i], cls=NumPyArangeEncoder)
            else:
                output = d[i]
            if isinstance(output,str):
                output = output.encode("utf-8")
            open(fname, "wb").write(output)


def run_file(module, filename, mbid=None):
    if not mbid:
        if filename.lower().endswith(".mp3"):
            md = compmusic.file_metadata(filename)
            mbid = md["meta"]["recordingid"]
    if mbid:
        module.musicbrainz_id = mbid
        ret = module.run(mbid, filename)
        save_data(module, ret)
    else:
        logging.error("Cannot find a mbid in this file. Use the mbid argument")



class Command(BaseCommand):
    help = 'Run a Dunya extractor'

    def add_arguments(self, parser):
        parser.add_argument('module', help='python module name of the extractor to run')
        parser.add_argument('file', help='path to the file to process')
        parser.add_argument('--mbid', required=False)

    def handle(self, *args, **options):
        mbid = options["mbid"]
        module = options["module"]
        file = options["file"]

        themod = load_module(module)
        if themod:
            run_file(themod, file, mbid)
        else:
            logger.error(f"Extractor module {module} could not be loaded")
