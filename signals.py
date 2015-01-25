__author__ = 'Wojciech Urbański'

import numpy as np
import numpy.fft as fft


class Signal():
    def __init__(self, signal_array, sample_frequency):
        self.signal = signal_array
        self._length = len(self.signal)
        self._sample_frequency = sample_frequency

    def _calculate_fft(self):
        spectrum = fft.fftshift(fft.fft(self.signal * np.blackman(self._length)))
        return spectrum[len(spectrum) / 2:] / np.max(np.abs(spectrum))

    def get_energy(self):
        return np.var(self.signal)

    def plot(self):
        timeline = np.arange(0, self._length/self._sample_frequency, 1/self._sample_frequency)
        return timeline, self.signal

    def plot_fft(self):
        freqline = fft.fftshift(fft.fftfreq(self._length, 1 / self._sample_frequency))
        return freqline[len(freqline) / 2:], 20 * np.log10(abs(self._calculate_fft()))
