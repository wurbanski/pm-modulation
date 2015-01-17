__author__ = 'Wojciech Urbanski'
import os
from system import *
from blocks import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc, rcParams


class PMApplication():
    _output_dir = "output"

    def __init__(self):
        self._setup()

    def _setup(self):
        self._modulator_freq = 10
        self._phase_dev = 1
        self._carrier_frequency = 50
        self._carrier_amplitude = 1
        self._sample_freq = 150
        self._simulation_time = 2
        self._BW = 2 * (self._carrier_frequency + self._phase_dev)
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
        rc('font', family='Arial')
        self._fft_limit = 0.01
        rcParams.update({'figure.autolayout': True})


    def run(self):
        self._setup()
        print("Ustawianie systemu bloków...")
        self._config = SystemConfiguration(self._simulation_time, self._sample_freq)

        blocks = [SineInputBlock(self._config, self._modulator_freq),
                  PhaseModulatorBlock(self._config, self._carrier_frequency,
                                      self._carrier_amplitude, self._phase_dev),
                  AWGNChannelBlock(self._config, snr=30),
                  PhaseDemodulatorBlock(self._config, carrier_freq=self._carrier_frequency,
                                        deviation=self._phase_dev),
                  LowPassFilterBlock(self._config, high_freq=self._BW / 2)]

        for block in blocks:
            self._config.add_block(block)

        self._config.connect_blocks()
        self._config.list_blocks()

        self._plot_stuff()
        self._plot_signal()
        self._plot_input_ffts()

    def _plot_stuff(self):
        timeline, values = self._config.blocks[0].output.plot()
        plt.plot(timeline, values, label="Modulator")
        timeline, values = self._config.blocks[1].output.plot()
        plt.plot(timeline, values, label="Modulowany")
        plt.legend()
        plt.show()
        plt.close()
        timeline, values = self._config.blocks[0].output.plot()
        plt.plot(timeline, values, label="input")
        timeline, values = self._config.blocks[-1].input.plot()
        plt.plot(timeline, values, label="input")
        timeline, values = self._config.blocks[-1].output.plot()
        plt.plot(timeline, values, label="Output")
        plt.legend()
        plt.show()
        plt.close()

    def _plot_signal(self):
        signal_plot = plt.figure(figsize=(8, 12))
        plt.tick_params(axis='both', which='major', labelsize="x-small")
        limit = 1.5 * np.max(self._config.blocks[2].output.signal)

        plt.subplot(511)
        plt.title("Sygnał modulujący")

        plt.subplot(512)
        plt.title("Sygnał zmodulowany")

        plt.subplot(513)
        plt.title("Sygnał za kanałem AWGN")

        plt.subplot(514)
        plt.title("Sygnał zdemodulowany")

        plt.subplot(515)
        plt.title("Sygnał odfiltrowany")

        for i in range(1, len(self._config.blocks) + 1):
            plt.subplot(5, 1, i)
            timeline, values = self._config.blocks[i - 1].output.plot()
            plt.plot(timeline, values)
            plt.ylim(-limit, limit)
            plt.grid(True)
            plt.xlabel("Czas [s]", fontsize="small")
            plt.ylabel("Wartość [V]", fontsize="small")

        plt.tight_layout()
        plt.show()
        signal_plot.savefig(os.path.join(self._output_dir, "signal.svg"))

    def _plot_input_ffts(self):

        fft_plot, subs = plt.subplots(2, figsize=(8, 8))

        for i in range(len(subs)):
            freqline, values = self._config.blocks[i].output.plot_fft()
            subs[i].set_title(self._config.blocks[i].name)
            subs[i].plot(freqline[values > self._fft_limit], values[values > self._fft_limit])
            subs[i].grid(True)
            subs[i].set_xlabel("Częstotliwość [Hz]", fontsize="small")
            subs[i].set_ylabel("Moduł widma", fontsize="small")

        # fft_plot.tight_layout()
        fft_plot.show()
        fft_plot.savefig(os.path.join(self._output_dir, "spectrum.svg"))

    def _general_setup(self):
        while True:
            try:
                self.time = float(input("Czas symulacji:"))
                self.sample_freq = float(input("Częstotliwość próbkowania:"))
                self.phase_dev = float(input("Dewiacja fazy:"))
            except ValueError:
                print("Nieprawidłowe dane wejściowe. Podaj dane ponownie.")
                continue
            else:
                break
        self._system = SystemConfiguration(time=self._time,
                                           sample_frequency=self._sample_freq,
                                           phase_dev=self._phase_dev)
        self._system.list_blocks()


if __name__ == '__main__':
    PMApplication().run()