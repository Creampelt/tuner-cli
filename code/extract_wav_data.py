"""Convert a .wav file to .csv

Uses the `wave` package to convert a .wav file to a .csv. 
Assumes that the file is monoaural (one channel).

Be sure to edit the code to point to correct values of `inFileName` and `outFileName`
"""

import wave
import numpy

inFileName = "../sound-files/ViolinG.wav"
outFileName = '../data/ViolinG.csv'

f = wave.open(inFileName, 'rb')
params = f.getparams()

print("There are {} frames.".format(params.nframes))

bytesData = f.readframes(params.nframes)
f.close()

a = numpy.frombuffer(bytesData, dtype=numpy.dtype('i2'))  # answer is an ndarray

i = 0

with open(outFileName, 'w') as out:

    out.write('i, time, sound\n')

    for val in a:
        time = 1000 * i / params.framerate  # milliseconds
        if time > 1000 / 220.0 * 10:
            break
        theLine = '{:g}, {:g}, {:g}\n'.format(i, time, val)
        out.write(theLine)
        i += 1

print("Wrote {} frames.".format(i))
