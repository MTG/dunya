import sys
import csv
import json

def main(fname):
    c = csv.reader(open(fname))
    items = {}
    single = {}
    for l in c:
        key, val, enkey, enval = l
        if key == "":
            mbid = single["recording"]["val"]
            items[mbid] = single
            single = {}
        else:
            entrim = enkey.lower().replace(" ", "").replace("-", "")
            single[entrim] = {"key": key, "val": val, "enkey": enkey, "enval": enval}
    if single:
        mbid = single["recording"]["val"]
        items[mbid] = single
    json.dump(items, open(sys.argv[2], "w"), indent=2)


if __name__ == "__main__":
    main(sys.argv[1])
