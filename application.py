__author__ = 'Wojciech Urbanski'
import os
from system import *
from blocks import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc


def finput(prompt):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Nieprawidłowa wartość!")
            continue
        else:
            return value


class PMApplication():
    _output_dir = "output"

    def __init__(self):
        self._setup()
        self._setup_environment()

    def _setup_environment(self):
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
        rc('font', family='Arial')
        self._fft_limit = -200

    def _setup(self):
        self._modulator_freq = 10
        self._phase_dev = 2
        self._carrier_frequency = 100
        self._carrier_amplitude = 1
        self._sample_freq = 64 * self._carrier_frequency
        self._simulation_time = 640 / self._carrier_frequency
        self._BW = 2 * (self._modulator_freq + self._phase_dev)
        self._snr = 15

    def _manual_setup(self):
        print("0 => Wartości domyślne (poniżej):")
        self._print_parameters()
        # do-while
        # validate each input against a set of rules
        while True:
            print()
            validate = -1
            while validate < 0:
                validate = finput("Szybkość próbkowania: ")
            self._sample_freq = validate if validate > 0 else 6400

            validate = -1
            while validate < 0 or validate > self._sample_freq / 2:
                validate = finput("Częstotliwość nośnej (0 - %.2f) : " % (self._sample_freq / 2))
            self._carrier_frequency = validate if validate > 0 else self._sample_freq / 64

            validate = -1
            while validate < 0 or validate > self._carrier_frequency / 2:
                validate = finput("Częstotliwość sygnału modulującego (0 - %.2f) : " % (self._carrier_frequency / 2))
            self._modulator_freq = validate if validate > 0 else self._carrier_frequency / 10

            validate = -1
            while validate < 0 or validate > np.pi:
                validate = finput("Dewiacja fazy (0-%.2f): " % np.pi)
            self._phase_dev = validate if validate > 0 else 1

            # break if LPF can be created
            if (self._carrier_frequency + self._BW) < self._sample_freq / 2:
                break
            # repeat if it cannot
            print("Zwiększ częstotliwość próbkowania, nie można utworzyć filtru.")

        validate = -1
        while validate < 0:
            validate = finput("Amplituda nośnej: ")
        self._carrier_amplitude = validate if validate > 0 else 1

        validate = -1
        while validate < 0 or validate < 1 / self._sample_freq and validate != 0:
            validate = finput("Czas symulacji (>%.2f): " % (1 / self._sample_freq))
        self._simulation_time = validate if validate > 0 else 64 / self._carrier_frequency

        validate = -1
        while validate < 0:
            validate = finput("SNR (>0): ")
        self._snr = validate if validate > 0 else 15
        self._BW = 2 * (self._modulator_freq + self._phase_dev)

    def run(self):
        # self._manual_setup()
        self._setup()
        self._print_parameters()
        print("Ustawianie systemu bloków...")
        self._config = SystemConfiguration(self._simulation_time, self._sample_freq)

        blocks_list = [
                       # NoiseGeneratorBlock(self._config, high_freq=self._modulator_freq),
                       SineGeneratorBlock(self._config, self._modulator_freq),
                       PhaseModulatorBlock(self._config, self._carrier_frequency,
                                           self._carrier_amplitude, self._phase_dev),
                       AWGNChannelBlock(self._config, snr=self._snr),
                       BandPassFilterBlock(self._config, low_freq=0.9*(self._carrier_frequency - self._BW/2),
                                           high_freq=1.1*(self._carrier_frequency + self._BW/2)),
                       PhaseDemodulatorBlock(self._config, frequency=self._carrier_frequency,
                                             deviation=self._phase_dev)]

        self._config.add_blocks(blocks_list)

        self._config.connect_blocks()
        self._config.list_blocks()

        self._plot_modulator()
        self._plot_outputs()
        self._plot_input_fft()
        self._plot_spectrograms()

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
            subplot.set_xlim(self._simulation_time/10, self._simulation_time/10 + 2/self._modulator_freq)
        signal_plot.set_tight_layout({"rect": (0, 0, 1, 0.96)})
        plt.show()
        signal_plot.savefig(os.path.join(self._output_dir, "signal.png"))

    def _plot_input_fft(self):
        fft_plot, subs = plt.subplots(len(self._config.blocks), figsize=(8, 12))
        fft_plot.suptitle("Wykresy widm Fouriera", fontsize="x-large")
        for i, subplot in enumerate(subs):
            freqline, values = self._config.blocks[i].output.plot_fft()
            low = np.min(np.where(values > self._fft_limit))
            high = np.max(np.where(values > self._fft_limit))
            if high-low < 20:
                low -= 20
                if low < 0:
                    low = 0
                high += 20
            subplot.set_title("Wyjście: %s" % self._config.blocks[i].name)
            subplot.plot(freqline, values, 'b')
            subplot.grid(True)
            subplot.set_xlabel("Częstotliwość [Hz]", fontsize="small")
            subplot.set_ylabel("Moduł widma [dB]", fontsize="small")
            subplot.axis('tight')
            subplot.set_xlim(0, 500)
            subplot.set_ylim(-80, 0)
        fft_plot.set_tight_layout({"rect": (0, 0, 1, 0.95)})
        plt.show()
        fft_plot.savefig(os.path.join(self._output_dir, "spectrum.png"))

    def _plot_modulator(self):
        signal_plot = plt.figure(figsize=(8, 4))
        plt.title("Porównanie sygnału wejściowego i wyjściowego", fontsize="x-large")
        plt.hold(True)
        timeline, values_in = self._config.blocks[0].output.plot()
        plt.plot(timeline, values_in, label="Sygnał modulujący")
        timeline, values_out = self._config.blocks[-1].output.plot()
        plt.plot(timeline, values_out, label="Sygnał zdemodulowany", alpha=0.5)
        plt.plot(timeline, values_in - values_out, 'r', label="Błąd demodulacji")
        plt.grid(True)
        plt.xlabel("Czas [s]", fontsize="small")
        plt.ylabel("Wartość [V]", fontsize="small")
        plt.legend(loc="best", fancybox=True, framealpha=0.5)
        plt.xlim(self._simulation_time/10, self._simulation_time/10 + 2/self._modulator_freq)
        plt.ylim(-1.1, 1.1)
        plt.show()
        signal_plot.savefig(os.path.join(self._output_dir, "signal_compare.png"))
        print("MSE: ", np.mean((values_in - values_out)**2))

    def _plot_spectrograms(self):
        spectrogram_plot, subplots = plt.subplots(3, figsize=(8, 12))
        plt.suptitle("Spektrogramy", fontsize="large")
        subplots[0].specgram(self._config.blocks[0].output.signal, Fs=self._sample_freq)
        subplots[0].set_title("na wyjściu generatora")
        subplots[1].specgram(self._config.blocks[2].output.signal, Fs=self._sample_freq)
        subplots[1].set_title("na wyjściu kanału AWGN")
        subplots[2].specgram(self._config.blocks[-1].output.signal, Fs=self._sample_freq)
        subplots[2].set_title("na wyjściu układu")
        spectrogram_plot.set_tight_layout({"rect": (0, 0, 1, 0.95)})
        for subplot in subplots:
            subplot.set_xlabel("czas [s]")
            subplot.set_ylabel("częstotliwość [Hz]")
            subplot.axis('tight')
            subplot.set_ylim(0, self._carrier_frequency + 10 * self._BW)
            subplot.set_xlim(self._simulation_time/10, self._simulation_time/10 + 2/self._modulator_freq)
            subplot.grid()
        plt.show()
        spectrogram_plot.savefig(os.path.join(self._output_dir, "spectrogram.png"))

    def _print_parameters(self):
        print("Szybkość próbkowania: %.2f samp/s" % self._sample_freq)
        print("Częstotliwość nośnej: %.2f Hz" % self._carrier_frequency)
        print("Częstotliwość modulatora: %.2f Hz" % self._modulator_freq)
        print("Dewiacja fazy: %.2f rad" % self._phase_dev)
        print("Amplituda nośnej: %.2f V" % self._carrier_amplitude)
        print("Czas symulacji: %.2f s" % self._simulation_time)
        print("Szerokość pasma sygnału: %.2f Hz" % self._BW)


if __name__ == '__main__':
    PMApplication().run()