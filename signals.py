__author__ = 'Wojciech Urbański'

import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt


def freqplot(signal_array, rate):
    freqline = np.arange(-rate / 2, rate / 2, rate / len(signal_array))
    plt.plot(freqline, signal_array)


class Signal():
    def __init__(self, signal_array):
        self.signal = signal_array
        self.time = len(self.signal)

    def get_fft(self):
        spectrum = fft.fftshift(fft.fft(self.signal * np.blackman(len(self.signal))))
        return spectrum / np.max(np.abs(spectrum))

    def get_energy(self):
        return np.var(self.signal)

    def plot(self, timeline=0, label="Signal"):
        if timeline is 0:
            timeline = np.arange(0, len(self.signal))
        plt.plot(timeline, self.signal, label=label)