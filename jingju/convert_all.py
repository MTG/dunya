import json
import os
import sys

from . import csvtojson, format_pitch


def main(fname):
    data = json.load(open(fname))
    for k, d in data.items():
        print(k)
        key = d["key"]["val"].lower()
        print(f" {key}")

        bname = f"data/{key}-banshi.csv"
        boutname = f"static/jingju/data/{k}-banshi.json"
        print(" banshi")
        if os.path.exists(bname):
            csvtojson.csvtojson(bname, boutname)

        lname = f"data/{key}-luogu.csv"
        loutname = f"static/jingju/data/{k}-luogu.json"
        print(" luogu")
        if os.path.exists(lname):
            csvtojson.csvtojson(lname, loutname)

        sname = f"data/{key}-syllables.csv"
        soutname = f"static/jingju/data/{k}-lyrics.json"
        print(" syllables")
        if os.path.exists(sname):
            csvtojson.csvtojson(sname, soutname)

        pname = f"data/{key}-pitch_track.csv"
        poutname = f"static/jingju/data/{k}-pitch.dat"
        phistoutname = f"static/jingju/data/{k}-histogram.json"
        print(" pitch")
        if os.path.exists(pname):
            tonic = d["First degree"]["val"].split(" ")[0]
            format_pitch.run(pname, tonic, poutname, phistoutname)
        print(k)


if __name__ == "__main__":
    main(sys.argv[1])
