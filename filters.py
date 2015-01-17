from scipy.signal import butter

__author__ = 'Wojciech Urbański'


def butter_lowpass(cutoff, fs, order=5, analog=False):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=analog)
    return b, a


def butter_bandpass(lowcut, highcut, fs, order=5, analog=True):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=analog)
    return b, a