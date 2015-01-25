import os
from scipy.signal import butter, lfilter

__author__ = 'Wojciech Urbański'


def butter_lowpass(cutoff, fs, order=5, analog=False):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=analog)
    return b, a


def butter_bandpass(lowcut, highcut, fs, order=5, analog=False):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band', analog=analog)
    return b, a


def plot_filter(b, a, threshold, lines):
    w, h = freqz(b, a)
    log_h = 20 * np.log10(abs(h))
    log_h_sel = log_h > threshold
    freq = (fs * 0.5 / np.pi) * w
    plot, subplots = plt.subplots(2, sharex=True, figsize=(8, 6))

    for subplot in subplots:
        for line in lines:
            subplot.axvline(line, color='k')

    subplots[0].set_title("Charakterystyka amplitudowa filtru")
    subplots[0].plot(freq[log_h_sel], log_h[[log_h_sel]])
    subplots[0].set_ylabel('Wzmocnienie [dB]')
    subplots[0].grid(True)
    subplots[1].set_title("Charakterystyka fazowa filtru")
    subplots[1].plot(freq[log_h_sel], np.angle(h)[log_h_sel], label="order = 5")
    subplots[1].set_xlabel('Częstotliwość [Hz]')
    subplots[1].set_ylabel('Faza [rad]')
    subplots[1].grid(True)
    plot.tight_layout()
    return plot


if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.signal import freqz
    from matplotlib import rc
    import os

    output_dir = "output"

    if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    rc('font', family='Arial')

    fs = 6400

    highcut = 15
    b, a = butter_lowpass(highcut, fs, analog=False)
    plot = plot_filter(b, a, -80, [highcut])
    plot.savefig(os.path.join("output", "lpfilter.png"))
    plt.close(plot)

    highcut = 120
    lowcut = 80
    b, a = butter_bandpass(0.9*lowcut, 1.1*highcut, fs, order=4)
    plot = plot_filter(b, a, -80, [lowcut, highcut])
    plot.savefig(os.path.join("output", "bpfilter.png"))
    plt.close(plot)