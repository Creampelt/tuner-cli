import numpy as np
from functools import reduce
import wave

DATA_FILE_NAME = "ViolinE"
MAX_ROWS = 2000
ERROR = 2000

NOTE_FREQUENCY_CHART = {
    415: "G#",
    440: "A",
    466: "A#",
    494: "B",
    523: "C",
    554: "C#",
    587: "D",
    622: "D#",
    659: "E",
    698: "F",
    740: "F#",
    784: "G",
    831: "G#",
    880: "A"
}


def get_local_max(arr):
    return reduce(lambda a, b: a if a["amplitude"] > b["amplitude"] else b, arr)


def extract_wav_data(data_file_name, max_rows=None):
    """
    Extracts data from a .wav file
    :param data_file_name: (String) the name of the .wav file (should be in /sound-files directory) without extension
    :param max_rows: (int or None) (optional) maximum number of data points to read from .wav file
    :return: (list) a list containing dictionaries {"index", "time" (ms), "amplitude"}
    """

    wav_file = wave.open("../sound-files/{}.wav".format(data_file_name))  # open .wav file
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


def get_frequency(data_file_name, max_rows=None):
    """
    Calculates the average frequency of a recording (.wav file)
    :param data_file_name: (String) the name of the .wav file (should be in /sound-files directory) without extension
    :param max_rows: (int or None) (optional) maximum number of data points to read from .wav file
    :return: (int) average frequency of recording in Hz
    """

    # 1. Get maximum value in data
    data = extract_wav_data(data_file_name, max_rows)  # data extracted from .wav; [{"index", "time", "amplitude"}]
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
        reduced_data.append(get_local_max(consecutive_data))  # add the local max of consecutive_data to reduced_data
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


def get_note_from_frequency(frequency):
    closest_note = min(NOTE_FREQUENCY_CHART, key=lambda note_freq: abs(note_freq - frequency))
    if closest_note == min(NOTE_FREQUENCY_CHART):
        return get_note_from_frequency(frequency * 2)
    if closest_note == max(NOTE_FREQUENCY_CHART):
        return get_note_from_frequency(frequency / 2)
    return NOTE_FREQUENCY_CHART[closest_note]


def get_note(data_file_name):
    frequency = get_frequency(data_file_name, MAX_ROWS)
    return get_note_from_frequency(frequency)


print("The note being played is {}{:g}.".format(get_note(DATA_FILE_NAME), get_frequency(DATA_FILE_NAME,
                                                                                        max_rows=MAX_ROWS)))
