from tuner import tuner
import argparse
import os
import sys
import re


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


parser = argparse.ArgumentParser(prog="tune",
                                 usage="%(prog)s [options] path",
                                 description="Calculate the pitch and frequency of .wav files")

parser.add_argument("path", type=str, help="the path to the audio file")
parser.add_argument("-t", "--tuner", action="store_true", help="use tuner mode")
parser.add_argument("-f", "--frequency", action="store_true", help="report frequency of pitch")
parser.add_argument("-a", "--setA", action="store", help="frequency to tune to in Hz (defaults to 440)")

args = parser.parse_args()

input_path = args.path
tuner_mode = args.tuner
report_frequency = args.frequency
a_frequency = args.setA if args.setA else 440


if not re.search(".*\.wav$", input_path):
    print("File must be in .wav format")
    sys.exit()
if not os.path.isfile(input_path):
    print("The specified audio file does not exist")
    sys.exit()
if not is_int(a_frequency) or int(a_frequency) < 400 or int(a_frequency) > 500:
    print("The A frequency must be an integer between 400 and 500")
    sys.exit()

a_frequency = int(a_frequency)
note = tuner.get_note(input_path, a_frequency, report_frequency)

print("The note being played is " + note)

if tuner_mode:
    intonation = tuner.get_intonation(input_path, a_frequency)
    if intonation == tuner.Intonation.IN_TUNE:
        print("Congrats! You're in tune, for once.")
    elif intonation == tuner.Intonation.SHARP:
        print("You're sharp. Not a surprise, I guess.")
    else:
        print("You're flat, like usual.")
