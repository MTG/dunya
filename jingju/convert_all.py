from __future__ import print_function

import json
import os
import sys

import csvtojson
import format_pitch


def main(fname):
    data = json.load(open(fname))
    for k, d in data.items():
        print(k)
        key = d["key"]["val"].lower()
        print(" %s" % key)

        bname = "data/%s-banshi.csv" % key
        boutname = "static/jingju/data/%s-banshi.json" % k
        print(" banshi")
        if os.path.exists(bname):
            csvtojson.csvtojson(bname, boutname)

        lname = "data/%s-luogu.csv" % key
        loutname = "static/jingju/data/%s-luogu.json" % k
        print(" luogu")
        if os.path.exists(lname):
            csvtojson.csvtojson(lname, loutname)

        sname = "data/%s-syllables.csv" % key
        soutname = "static/jingju/data/%s-lyrics.json" % k
        print(" syllables")
        if os.path.exists(sname):
            csvtojson.csvtojson(sname, soutname)

        pname = "data/%s-pitch_track.csv" % key
        poutname = "static/jingju/data/%s-pitch.dat" % k
        phistoutname = "static/jingju/data/%s-histogram.json" % k
        print(" pitch")
        if os.path.exists(pname):
            tonic = d["First degree"]["val"].split(" ")[0]
            format_pitch.run(pname, tonic, poutname, phistoutname)
        print(k)


if __name__ == "__main__":
    main(sys.argv[1])
