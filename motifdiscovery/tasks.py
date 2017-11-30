from __future__ import print_function

import math
import os
import subprocess
import wave

from django.db import transaction

from docserver import util
from dunya.celery import app
from motifdiscovery import models

ROOT_DIR = "/incoming/motifdiscovery"


@app.task
def convert_mp3(file_id):
    thefile = models.File.objects.get(pk=file_id)
    segments = thefile.segment_set.all()
    numsegs = segments.count()
    with transaction.atomic():
        for i, s in enumerate(segments, 1):
            if i % 100 == 0:
                print("  - [%s]: Done %s/%s" % (file_id, i, numsegs))
            inname = s.segment_path
            inname = inname[:-3] + "wav"
            outname = inname[:-3] + "mp3"
            if os.path.exists(outname):
                continue
            args = ["ffmpeg", "-i", inname, outname]
            proc = subprocess.Popen(args, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
            proc.communicate()
            s.segment_path = outname
            s.save()
            os.unlink(inname)


@app.task
def fix_segments(file_id):
    thefile = models.File.objects.get(pk=file_id)
    patterns = thefile.pattern_set.all()
    wav_file, wav_created = util.docserver_get_wav_filename(thefile.mbid)
    print("Making segments for file %s" % thefile)
    numpat = len(patterns)
    print("Got %s segments to do" % numpat)
    wav_in = wave.open(wav_file, 'rb')
    params = wav_in.getparams()
    samplerate = wav_in.getframerate()

    with transaction.atomic():
        for i, p in enumerate(patterns, 1):
            if i % 100 == 0:
                print("  - [%s]: Done %s/%s" % (file_id, i, numpat))
            r_start = round(p.start_time, 1)
            r_end = round(p.end_time, 1)
            qs = models.Segment.objects.filter(file=thefile, rounded_start=r_start, rounded_end=r_end)
            if qs.exists():
                start_str = str(r_start)
                end_str = str(r_end)
                fname = "%s-%s.wav" % (start_str, end_str)
                dname = start_str[0]

                full_dir = os.path.join(ROOT_DIR, str(thefile.id), dname)
                full_path = os.path.join(full_dir, fname)
                mp3_path = full_path[:-3] + "mp3"

                if os.path.exists(mp3_path) and os.stat(mp3_path).st_size == 0:
                    print("deleting %s" % mp3_path)
                    os.unlink(mp3_path)
                    sframe = int(math.floor(r_start * samplerate))
                    eframe = int(math.ceil(r_end * samplerate))
                    wav_in.setpos(sframe)
                    frames = wav_in.readframes(eframe - sframe)

                    wav_out = wave.open(full_path, 'wb')
                    wav_out.setparams(params)
                    wav_out.writeframes(frames)

    if wav_created:
        os.unlink(wav_file)


@app.task
def make_segments(file_id):
    thefile = models.File.objects.get(pk=file_id)
    patterns = thefile.pattern_set.all()
    wav_file, wav_created = util.docserver_get_wav_filename(thefile.mbid)
    print("Making segments for file %s" % thefile)
    numpat = len(patterns)
    print("Got %s segments to do" % numpat)
    wav_in = wave.open(wav_file, 'rb')
    params = wav_in.getparams()
    samplerate = wav_in.getframerate()

    with transaction.atomic():
        for i, p in enumerate(patterns, 1):
            if i % 100 == 0:
                print("  - [%s]: Done %s/%s" % (file_id, i, numpat))
            r_start = round(p.start_time, 1)
            r_end = round(p.end_time, 1)
            qs = models.Segment.objects.filter(file=thefile, rounded_start=r_start, rounded_end=r_end)
            if qs.exists():
                # we already have a segment for this start time and end time
                s = qs.get()
                p.segment = s
                p.save()
            else:
                start_str = str(r_start)
                end_str = str(r_end)
                fname = "%s-%s.wav" % (start_str, end_str)
                dname = start_str[0]

                full_dir = os.path.join(ROOT_DIR, str(thefile.id), dname)
                full_path = os.path.join(full_dir, fname)
                try:
                    os.makedirs(full_dir)
                except os.error:
                    pass

                sframe = int(math.floor(r_start * samplerate))
                eframe = int(math.ceil(r_end * samplerate))
                wav_in.setpos(sframe)
                frames = wav_in.readframes(eframe - sframe)

                # create the file, save it, add a entry
                # args = ["ffmpeg", "-i", wav_file, "-ss", str(r_start), "-t", str((r_end-r_start)), full_path]
                # proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                # proc.communicate()
                wav_out = wave.open(full_path, 'wb')
                wav_out.setparams(params)
                wav_out.writeframes(frames)
                s = models.Segment.objects.create(file=thefile, rounded_start=r_start, rounded_end=r_end,
                                                  segment_path=full_path)
                p.segment = s
                p.save()

    if wav_created:
        os.unlink(wav_file)
