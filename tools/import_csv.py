#!/usr/bin/env python

import csv
import sys
import os
import argparse
sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), ".."))

from dunya import settings
from django.core.management import setup_environ
setup_environ(settings)

from carnatic.models import *
import data.models


def load(fname, obclass):
    """ Load a csv file into a class. If any items are in 
    additional columns then import them as aliases """
    fp = open(fname, "rb")
    reader = csv.reader(fp)
    for line in reader:
        name = line[0]
        rest = line[1:]
        item, _ = obclass.objects.get_or_create(name=name)
        if hasattr(obclass, "aliases"):
            for a in rest:
                if a:
                    item.aliases.create(name=a)

def main(args):
    obclass = aliasclass = None
    t = args.t
    fname = args.fname
    if t == "instrument":
        obclass = Instrument
    elif t == "raaga":
        obclass = Raaga
    elif t == "taala":
        obclass = Taala
    elif t == "region":
        obclass = GeographicRegion
    if obclass:
        load(fname, obclass)

if __name__ == "__main__":
    choices = ["instrument", "raaga", "taala", "region"]
    p = argparse.ArgumentParser(description="Load data csv")
    p.add_argument("-t", required=True, choices=choices)
    p.add_argument("fname", help="The zip file to import")
    args = p.parse_args()

    main(args)
