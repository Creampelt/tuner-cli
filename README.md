Tuner CLI (previously WAV to Pitch Project)
===========================================

**Goal**: Determine the average frequency (Hz) and pitch (music note) in a given recording

Background Information
----------------------

Some things you might need to know about a sound wave:
* **Frequency**: # of periods in a given amount of time (usually measured in Hz or s<sup>-1</sup>)
    * Correlates to pitch; &uarr; frequency &rarr; &uarr; pitch
    * Octaves = 2x (A440, A220, A880, etc.)
* **Amplitude**: The height of one crest/trough
    * Correlates to volume; &uarr; amplitude &rarr; &uarr; volume
* Sound wave = sinusoid
    * y = [amp]sin([freq]x/1000pi)

Process
-------

The approach I took to go from a WAV file to a note was:
1. Isolate the crests
    1. Find max value in data
    2. Filter to all values within a certain range (`ERROR`) of the max (I used `ERROR = 2000`)
    3. Filter to local maxes to find the top of each crest
2. Get the average period
    1. Find the difference between each point
    2. Average the differences
3. Convert to Hz (ms &rarr; ms<sup>-1</sup> &rarr; s<sup>-1</sup> = Hz)
4. Map to music note
    1. Multiply or divide by 2 until correct octave is reached
    2. Find closest frequency

I used this method, in which you essentially "chop off" the tops of each crest, in order to isolate the major crests
from the smaller ones.

Result
------

### Data

| Note | Expected (Hz) | Result (Hz) |
|:----:|:-------------:|:-----------:|
| A    | 441           | 441         |
| D    | 293           | 294         |
| G    | 196           | 97          |
| E    | 659           | 659         |

### Analysis

* **Pros**
    * Generally works very well
    * If `ERROR` is set correctly, it works very well
* **Cons**
    * Assumes that amplitude is generally constant
    * `ERROR` must be adjusted manually
