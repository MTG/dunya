
from dunya.celery import app
from motifdiscovery import models
from docserver import util
import os
import subprocess

ROOT_DIR = "/incoming/motifdiscovery"

@app.task
def make_segments(file_id):
    thefile = models.File.objects.get(pk=file_id)
    patterns = f.pattern_set.all()
    wav_file, wav_created = util.docserver_get_wav_filename(f.mbid)
    print "Making segments for file %s" % thefile
    print "Got %s segments to do" % len(patterns)
    for i, p in enumerate(patterns, 1):
        if i % 100 == 0:
            print "  - Done 100"
        r_start = round(p.start_time, 1)
        r_end = round(p.end_time, 1)
        qs = models.Segment.objects.filter(file=f, rounded_start=r_start, rounded_end=r_end)
        if qs.exists()
            # we already have a segment for this start time and end time
            s = qs.get()
            p.segment = s
            p.save()
        else:
            start_str = str(r_start)
            end_str = str(r_end)
            fname = "%s-%s.mp3" % (start_str, end_str)
            dname = start_str[0]
            
            full_dir = os.path.join(ROOT_DIR, str(thefile.id), dname)
            full_path = os.path.join(full_dir, fname)
            try:
                os.makedirs(full_dir)
            except os.error:
                pass

            # create the file, save it, add a entry
            args = ["ffmpeg", "-i", wav_file, "-ss", r_start, "-t", (r_end-r_start), full_path]
            proc = subprocess.Popen(proclist)
            proc.communicate()
            s = models.Segment.objects.create(file=f, rounded_start=r_start, rounded_end=r_end, segment_path=full_path)
            p.segment = s
            p.save()

    if wav_created:
        os.unlink(wav_file)
