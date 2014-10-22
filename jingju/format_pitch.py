
import sys
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import StringIO
import struct
import json

## Most of this from NormalisePitch in the pitch extractor

def interpolatePitchTracks(timeArrIn, pitchArrIn, timeArrOut, SilVal):
    ind = np.where(pitchArrIn<=SilVal)[0]
    pitchArrIn[ind] = SilVal
    pitchArrOut = np.interp(timeArrOut, timeArrIn, pitchArrIn)

    #now deadling with silence regions
    indSil = np.where(pitchArrIn<=SilVal)[0]

    interpFactor = float(timeArrIn[1]-timeArrIn[0])/(timeArrOut[1]-timeArrOut[0])

    indSilNew1 = np.floor(indSil*interpFactor).astype(np.int)
    indSilNew2 = np.ceil(indSil*interpFactor).astype(np.int)

    indSil = np.intersect1d(indSilNew1, indSilNew2)

    return pitchArrOut

def get_histogram(pitch, nbins, smoothness=1):
    valid_pitch = [p for p in pitch if p > 0]
    bins = [i-0.5 for i in range(0, nbins+1)]
    histogram, edges = np.histogram(valid_pitch, bins, density=True)
    smoothed = gaussian_filter(histogram, smoothness)

    return smoothed

def normalise_pitch(pitch, tonic, bins_per_octave, max_value):
    eps = np.finfo(np.float).eps
    normalised_pitch = bins_per_octave * np.log2(2.0 * (pitch+eps) / tonic)
    indexes = np.where(normalised_pitch <= 0)
    normalised_pitch[indexes] = 0
    indexes = np.where(normalised_pitch > max_value)
    normalised_pitch[indexes] = max_value
    return normalised_pitch

def run(fname, tonic):
    tonic = float(tonic)

    nppitch = np.loadtxt(fname, delimiter=",")
    bpo = 85 # 255 pixel high image spanning 3 octaves = 85px/octave
    height = 255 # Height of the image

    lastTimestamp = nppitch[-1,0]
    outputTime = np.arange(0, lastTimestamp, 196/44100.0)
    resampled = interpolatePitchTracks(nppitch[:,0], nppitch[:,1], outputTime, 0)

    drawpitch = normalise_pitch(resampled, tonic, bpo, height)
    packed_pitch = StringIO.StringIO()
    for p in drawpitch:
        packed_pitch.write(struct.pack("B", p))
    drawhist = get_histogram(drawpitch, 256, 1)

    pp = packed_pitch.getvalue()
    print type(drawhist)

    open("pitch.dat", "w").write(pp)
    open("hist.dat", "w").write(json.dumps(drawhist.tolist()))

if __name__ == "__main__":
    if len(sys.argv) > 2:
        run(sys.argv[1], sys.argv[2])
