import csv
import json
import sys
import codecs

def main(fname):
    c = open(fname).readlines()
    out = []
    for l in c:
        l = l.strip().split(",")
        out.append([l[0], round(float(l[1]), 0), round(float(l[2]), 0)])
    print json.dumps(out)

if __name__ == "__main__":
    main(sys.argv[1])
