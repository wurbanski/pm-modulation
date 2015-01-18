import os
from scipy.signal import butter, lfilter

__author__ = 'Wojciech Urbański'


def butter_lowpass(cutoff, fs, order=5, analog=False):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=analog)
    return b, a


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz
    from matplotlib import rc

    rc('font', family='Arial')

    fs = 6400

    highcut = 224
    plot, subplots = plt.subplots(2, sharex=True, figsize=(8, 8))
    b, a = butter_lowpass(highcut, fs, analog=False)
    w, h = freqz(b, a)
    subplots[0].set_title("Charakterystyka amplitudowa filtru")
    subplots[0].plot((fs * 0.5 / np.pi) * w, abs(h))
    subplots[0].axvline(highcut, color='k')
    subplots[0].set_ylabel('Wzmocnienie [dB]')
    subplots[0].grid(True)

    subplots[1].set_title("Charakterystyka fazowa filtru")
    subplots[1].plot((fs * 0.5 / np.pi) * w, np.angle(h), label="order = 5")
    subplots[1].axvline(highcut, color='k')
    subplots[1].set_xlabel('Częstotliwość [Hz]')
    subplots[1].set_ylabel('Faza [rad]')
    subplots[1].grid(True)

    plot.tight_layout()
    plot.show()
    plot.savefig(os.path.join("output", "filter.png"))