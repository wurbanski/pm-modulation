__author__ = 'Wojciech Urbański'

import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt


class Signal():
    def __init__(self, signal_array, sample_frequency):
        self.signal = signal_array
        self.length = len(self.signal)
        self.sample_frequency = sample_frequency

    def _calculate_fft(self):
        spectrum = fft.fftshift(fft.fft(self.signal))
        return spectrum / np.max(np.abs(spectrum))

    def get_energy(self):
        return np.var(self.signal)

    def plot(self):
        timeline = np.arange(0, self.length/self.sample_frequency, 1/self.sample_frequency)
        return timeline, self.signal

    def plot_fft(self):
        freqline = fft.fftshift(fft.fftfreq(self.length, 1 / self.sample_frequency))
        return freqline, 20 * np.log10(abs(self._calculate_fft()))
