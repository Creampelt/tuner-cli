import numpy as np
from functools import reduce
import wave
from math import log
from enum import Enum

MAX_ROWS = 2000
ERROR = 2000

A_CONST = 2 ** (1.0 / 12)
NOTES = ["A", "A#/Bb", "B", "C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab"]
INTONATION_ERROR = 0.03


class Intonation(Enum):
    FLAT = -1
    IN_TUNE = 0
    SHARP = 1


def _get_local_max(arr):
    """
    Returns the maximum value in a list of data
    :param arr: a list of values to compare
    :return: maximum value in arr
    """
    return reduce(lambda a, b: a if a["amplitude"] > b["amplitude"] else b, arr)


def _extract_wav_data(data_file_name, max_rows=None):
    """
    Extracts data from a .wav file
    :param data_file_name: the path to the .wav file
    :param max_rows: (optional) maximum number of data points to read from .wav file
    :return: a list containing dictionaries {"index", "time" (ms), "amplitude"}
    """

    wav_file = wave.open(data_file_name)  # open .wav file
    params = wav_file.getparams()  # get params of .wav file (e.g. framerate, number of frames, etc.)
    bytes_data = wav_file.readframes(params.nframes)  # reads the .wav file (as a string of bytes)
    wav_file.close()  # done reading .wav file

    a = np.frombuffer(bytes_data, dtype=np.dtype("i2"))  # gets an ndarray (i.e. iterable) from .wav data
    data = []
    for i, amp in enumerate(a):
        # breaks out of loop if data has exceeded max_rows
        if max_rows is not None and i >= max_rows:
            break
        time = 1000 * i / params.framerate  # time in milliseconds
        data_row = {"index": i, "time": time, "amplitude": amp}  # data to push to final array
        data.append(data_row)
    return data


def _get_frequency(data_file_name, max_rows=None):
    """
    Calculates the average frequency of a recording (.wav file)
    :param data_file_name: the name of the .wav file (should be in /sound-files directory) without extension
    :param max_rows: (optional) maximum number of data points to read from .wav file
    :return: average frequency of recording in Hz
    """

    # 1. Get maximum value in data
    data = _extract_wav_data(data_file_name, max_rows)  # data extracted from .wav; [{"index", "time", "amplitude"}]
    max_value = reduce(lambda a, b: a if a["amplitude"] > b["amplitude"] else b, data)["amplitude"]  # (float) maximum
    # amplitude in .wav data

    # 2. Filter data to only points within ERROR (1500) of the max value
    peak_data = list(filter(lambda row: row["amplitude"] + ERROR >= max_value, data))

    # 3. Get local maxes for all consecutive values (i.e. get the peak of each cycle)
    reduced_data = []
    i = 1  # start at index 1 (to avoid indexing error)
    consecutive_data = [peak_data[0]]  # start consecutive_data with 0th term in order to include in reduced_data
    while i < len(peak_data):
        consecutive = peak_data[i - 1]["index"] + 1 == peak_data[i]["index"]
        # add all consecutive values to consecutive_data
        while consecutive and i < len(peak_data) - 1:
            consecutive_data.append(peak_data[i - 1])
            i += 1
            consecutive = peak_data[i - 1]["index"] + 1 == peak_data[i]["index"]
        consecutive_data.append(peak_data[i - 1])  # add last value to consecutive_data
        reduced_data.append(_get_local_max(consecutive_data))  # add the local max of consecutive_data to reduced_data
        consecutive_data = []
        i += 1

    # 4. Calculate average time between data points
    differences = []
    for i, data_row in enumerate(reduced_data[1:], start=1):
        differences.append(data_row["time"] - reduced_data[i - 1]["time"])
    avg_time = np.mean(differences)

    # 5. Calculate frequency; f = 10^3 / avg_time
    frequency = (10 ** 3) / avg_time
    return int(np.round(frequency))


def _calculate_n(fn, f0):
    """
    Calculates the number of half steps from f0 (frequency for A) to the given note.
    Derived from formula: f_n = f_0 * a^n (where a = 2^(1/12) and n is # of half steps from f_0)
    :param fn: frequency in Hz of note in question
    :param f0: frequency in Hz of baseline note
    :return: # of half steps between f0 and fn
    """
    return log(fn / float(f0), A_CONST)


def _get_note_from_steps(n):
    """
    Gets letter note from distance (in half steps) between A and note
    :param n: number of half steps from note in question to A4
    :return: Letter value of note (ex: "A", "C#/Db", etc.)
    """
    if n < 0:
        return _get_note_from_steps(n + 12)
    elif n >= len(NOTES):
        return _get_note_from_steps(n - 12)
    else:
        return NOTES[n]


def _get_note_from_frequency(frequency, f0):
    """
    Gets letter note from given frequency
    :param frequency: frequency in Hz of note in question
    :param f0: frequency of A4 (usually 440 or 441)
    :return: Letter note of provided frequency
    """
    n = round(_calculate_n(frequency, f0))
    return _get_note_from_steps(n)


def get_intonation(data_file_name, f0=440):
    """
    Determines whether the note in a given data file is in tune, sharp, or flat
    :param data_file_name: .wav file to open
    :param f0: frequency of A4 (usually 440 or 441)
    :return: a value from the Intonation enum (FLAT, IN_TUNE, or SHARP)
    """
    frequency = _get_frequency(data_file_name, MAX_ROWS)
    n = _calculate_n(frequency, f0)
    if n - round(n) < -1 * INTONATION_ERROR:
        return Intonation.FLAT
    elif n - round(n) > INTONATION_ERROR:
        return Intonation.SHARP
    else:
        return Intonation.IN_TUNE


def get_note(data_file_name, f0=440, include_freq=False):
    """
    Gets the note being played in a given .wav file
    :param data_file_name: .wav file to open
    :param f0: frequency of A4 (usually 440 or 441)
    :param include_freq: whether to include frequency in returned string
    :return: note being played (ex: "A", "C#/Db"). If include_freq, then note will be formatted as "A440", etc.
    """
    frequency = _get_frequency(data_file_name, MAX_ROWS)
    note = _get_note_from_frequency(frequency, f0)
    if include_freq:
        return "{}{}".format(note, frequency)
    else:
        return note
