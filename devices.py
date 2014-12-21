__author__ = 'Wojciech'

import numpy as np
import scipy as sp
import numpy.fft as fft


class SystemConfiguration():
    blocks = []

    def __init__(self, time=1, rate=1):
        self.timeline = np.arange(0, time, 1/rate)

    def add_block(self, block, position=-1):
        if -1 >= position:
            self.blocks.insert(position, block)
        else:
            self.blocks.append(block)

    def list_blocks(self):
        print('Total blocks: ', len(self.blocks))
        for block in self.blocks:
            print('Block ', self.blocks.index(block), ': ', block.name())



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
        self.signal_out = self.process(self.signal_in)

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
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config)

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self.config.timeline * self.frequency))

    def name(self):
        return "This is an InputBlock."


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1):
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config)

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self.frequency * self.config.timeline + signal_in.signal))

    def name(self):
        return "This is a PhaseModulator Block."


class AWGNChannelBlock(Block):
    def __init__(self, config, snr=20):
        super().__init__(config)
        self.snr = snr

    def process(self, signal_in):
        var = signal_in.get_energy()
        sigma = np.sqrt(var) * 10 ** (-self.snr / 20)
        noise = np.random.normal(loc=0.0, scale=sigma, size=self.config.timeline.shape)
        return Signal(signal_in.signal + noise)