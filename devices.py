__author__ = 'Wojciech'

import numpy as np
import scipy as sp
import numpy.fft as fft


class SystemConfiguration():
    blocks = []

    def __init__(self, rate=1, time=1):
        self.timeline = np.arange(0, time, rate)

    def add_block(self, block, position=-1):
        if -1 >= position:
            self.blocks.insert(position, block)
        else:
            self.blocks.append(block)


class Signal():
    def __init__(self, signal_array):
        self.signal = signal_array

    def get_fft(self):
        spectrum = fft.fftshift(fft.fft(self.signal * np.blackman(np.len(self.signal))))
        return spectrum / np.max(np.abs(spectrum))

    def get_energy(self):
        return np.var(self.signal)


class Block():
    def __init__(self, config):
        self.config = config
        self.signal_in = Signal(np.zeros(self.config.timeline.shape))
        self.signal_out = Signal(np.zeros(self.config.timeline.shape))

    def input(self, previous_block):
        self.signal_in = previous_block.output()
        self.signal_out = self.process(self.signal_in)

    def process(self, signal_in):
        return signal_in

    def output(self):
        return self.signal_out

    @property
    def name(self):
        return "Generic block"


class InputBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1):
        super().__init__(config)
        self.frequency = frequency
        self.amplitude = amplitude

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self.config.timeline * self.frequency))


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1):
        super().__init__(config)
        self.frequency = frequency
        self.amplitude = amplitude

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self.frequency * self.config.timeline + signal_in.signal))


class AWGNChannelBlock(Block):
    def __init__(self, config, snr=20):
        super().__init__(config)
        self.snr = snr

    def process(self, signal_in):
        var = signal_in.get_energy()
        sigma = np.sqrt(var) * 10 ** (-self.snr / 20)
        noise = np.random.normal(loc=0.0, scale=sigma, size=self.config.timeline.shape)
        return Signal(signal_in.signal + noise)