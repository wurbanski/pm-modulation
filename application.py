__author__ = 'Wojciech Urbanski'
import os
from system import *
from blocks import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc


class PMApplication():
    _output_dir = "output"

    def __init__(self):
        self._setup_environment()
        self._setup()

    def _setup_environment(self):
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
        rc('font', family='Arial')
        self._fft_limit = -30

    def _setup(self):
        self._modulator_freq = 10
        self._phase_dev = 2
        self._carrier_frequency = 100
        self._carrier_amplitude = 1
        self._sample_freq = 64 * self._carrier_frequency
        self._simulation_time = 64 / self._carrier_frequency
        self._BW = 2 * (self._modulator_freq + self._phase_dev)
        self._snr = 8

    def run(self):
        self._setup()
        self._print_parameters()
        print("Ustawianie systemu bloków...")
        self._config = SystemConfiguration(self._simulation_time, self._sample_freq)

        blocks_list = [SineInputBlock(self._config, self._modulator_freq),
                       PhaseModulatorBlock(self._config, self._carrier_frequency,
                                           self._carrier_amplitude, self._phase_dev),
                       AWGNChannelBlock(self._config, snr=self._snr),
                       LowPassFilterBlock(self._config, high_freq=2 * (self._carrier_frequency + self._BW / 2)),
                       PhaseDemodulatorBlock(self._config, carrier_freq=self._carrier_frequency,
                                             deviation=self._phase_dev)]

        self._config.add_blocks(blocks_list)

        self._config.connect_blocks()
        self._config.list_blocks()

        self._plot_outputs()
        self._plot_input_ffts()
        self._plot_spectrograms()
        self._plot_modulator()

        print("Rzeczywisty SNR: ", self._config.blocks[2].get_snr())

    def _plot_outputs(self):
        signal_plot, subplots = plt.subplots(len(self._config.blocks), figsize=(8, 12))
        signal_plot.suptitle("Przebiegi czasowe sygnału", fontsize="x-large")
        for i, subplot in enumerate(subplots):
            timeline, values = self._config.blocks[i].output.plot()
            subplot.plot(timeline, values)
            subplot.grid(True)
            subplot.set_xlim(0, np.max(self._config.timeline))
            subplot.set_xlabel("Czas [s]", fontsize="small")
            subplot.set_ylabel("Wartość [V]", fontsize="small")
            subplot.set_title("Wyjście: %s" % self._config.blocks[i].name)
        signal_plot.set_tight_layout({"rect": (0, 0, 1, 0.96)})
        plt.show()
        signal_plot.savefig(os.path.join(self._output_dir, "signal.png"))

    def _plot_input_ffts(self):
        fft_plot, subs = plt.subplots(len(self._config.blocks), figsize=(8, 12))
        fft_plot.suptitle("Wykresy widm Fouriera", fontsize="x-large")
        for i, subplot in enumerate(subs):
            freqline, values = self._config.blocks[i].output.plot_fft()
            subplot.set_title("Wyjście: %s" % self._config.blocks[i].name)
            subplot.plot(freqline[values > self._fft_limit], values[values > self._fft_limit], 'b')
            subplot.grid(True)
            subplot.set_xlabel("Częstotliwość [Hz]", fontsize="small")
            subplot.set_ylabel("Moduł widma [dB]", fontsize="small")
            subplot.axis('tight')
        fft_plot.set_tight_layout({"rect": (0, 0, 1, 0.95)})
        plt.show()
        fft_plot.savefig(os.path.join(self._output_dir, "spectrum.png"))

    def _plot_modulator(self):
        signal_plot = plt.figure(figsize=(8, 4))
        plt.title("Porównanie sygnału wejściowego i wyjściowego", fontsize="x-large")
        plt.hold(True)
        timeline, values_in = self._config.blocks[0].output.plot()
        plt.plot(timeline, values_in, label="Modulator")
        timeline, values_out = self._config.blocks[-1].output.plot()
        plt.plot(timeline, values_out, label="Zdemodulowany", alpha=0.5)
        plt.plot(timeline, values_in - values_out, 'r', label="Błąd demodulacji", alpha=0.6)
        plt.grid(True)
        plt.xlabel("Czas [s]", fontsize="small")
        plt.ylabel("Wartość [V]", fontsize="small")
        plt.legend(loc="best", fancybox=True, framealpha=0.5)
        plt.xlim(0, np.max(timeline))
        plt.show()
        signal_plot.savefig(os.path.join(self._output_dir, "signal_compare.png"))

    def _plot_spectrograms(self):
        spectrogram_plot, subplots = plt.subplots(3, figsize=(8, 12))
        plt.suptitle("Spektrogramy", fontsize="large")
        subplots[0].specgram(self._config.blocks[0].output.signal, Fs=self._sample_freq)
        subplots[0].set_xlabel("czas [s]")
        subplots[0].set_ylabel("częstotliwość [Hz]")
        subplots[0].axis('tight')
        subplots[0].grid()
        subplots[0].set_title("na wyjściu generatora")
        subplots[1].specgram(self._config.blocks[2].output.signal, Fs=self._sample_freq)
        subplots[1].set_xlabel("czas [s]")
        subplots[1].set_ylabel("częstotliwość [Hz]")
        subplots[1].axis('tight')
        subplots[1].grid()
        subplots[1].set_title("na wyjściu kanału AWGN")
        subplots[2].specgram(self._config.blocks[-1].output.signal, Fs=self._sample_freq)
        subplots[2].set_xlabel("czas [s]")
        subplots[2].set_ylabel("częstotliwość [Hz]")
        subplots[2].axis('tight')
        subplots[2].grid()
        subplots[2].set_title("na wyjściu układu")
        spectrogram_plot.set_tight_layout({"rect": (0, 0, 1, 0.95)})
        plt.show()
        spectrogram_plot.savefig(os.path.join(self._output_dir, "spectrogram.png"))

    def _print_parameters(self):
        print("Częstotliwość modulatora: %.2f Hz" % self._modulator_freq)
        print("Dewiacja fazy: %.2f rad" % self._phase_dev)
        print("Częstotliwość nośnej: %.2f Hz" % self._carrier_frequency)
        print("Amplituda nośnej: %.2f V" % self._carrier_amplitude)
        print("Częstotliwość próbkowania: %.2f sam/s" % self._sample_freq)
        print("Czas symulacji: %.2f s" % self._simulation_time)
        print("Szerokość pasma sygnału: %.2f Hz" % self._BW)


if __name__ == '__main__':
    PMApplication().run()