__author__ = 'Wojciech Urbański'

import numpy as np
import scipy as sp
import numpy.fft as fft
import matplotlib.pyplot as plt


def freqplot(signal_array, rate):
    freqline = np.arange(-rate/2, rate/2, rate/len(signal_array))
    plt.plot(freqline, signal_array)


class SystemConfiguration():
    blocks = []

    def __init__(self, time=1, rate=1):
        self.timeline = np.arange(0, time, 1/rate)
        self.time = time
        self.rate = rate

    def add_block(self, block, position=-1):
        if isinstance(block, Block):
            if -1 > position:
                self.blocks.insert(position, block)
            else:
                self.blocks.append(block)
        else:
            raise TypeError("Specified element is not of 'Block' type")

    def list_blocks(self):
        print('Total blocks: ', len(self.blocks))
        for block in self.blocks:
            print('Block ', self.blocks.index(block), ': ', block.name, sep='')

    def refresh_blocks(self):
        for i in range(1, len(self.blocks)):
            print(i - 1, self.blocks[i - 1].name, 'to', i, self.blocks[i].name)
            self.blocks[i].connect(self.blocks[i - 1])

    def get_block(self, i):
        if i < len(self.blocks):
            return self.blocks[i]
        else:
            raise ValueError("No block of specified type exists.")


class Signal():
    def __init__(self, signal_array):
        self.signal = signal_array

    def get_fft(self):
        spectrum = fft.fftshift(fft.fft(self.signal * np.blackman(len(self.signal))))
        return spectrum / np.max(np.abs(spectrum))

    def get_energy(self):
        return np.var(self.signal)


class Block():
    def __init__(self, config, name="Generic Block"):
        self.config = config
        self.__signal_in = Signal(np.zeros(self.config.timeline.shape))
        self.__signal_out = self.process(self.__signal_in)
        self.__name = name

    def connect(self, previous_block):
        if isinstance(previous_block, Block):
            self.__signal_in = previous_block.output
            self.__signal_out = self.process(self.__signal_in)
        else:
            raise TypeError("Wrong type, cannot connect.")

    def process(self, signal_in):
        pass

    @property
    def input(self):
        return self.__signal_in

    @property
    def output(self):
        return self.__signal_out

    @property
    def name(self):
        return self.__name


class SineInputBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, name="Sine Input"):
        self._frequency = frequency
        self._amplitude = amplitude
        super().__init__(config, name)

    def process(self, signal_in):
        return Signal(self._amplitude * np.sin(self.config.timeline * self._frequency))


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, name="Phase Modulator"):
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config, name)

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self.frequency * self.config.timeline + signal_in.signal))


class AWGNChannelBlock(Block):
    def __init__(self, config, snr=20, name="AWGN Channel"):
        self._snr = snr
        super().__init__(config, name)

    def process(self, signal_in):
        var = signal_in.get_energy()
        if var > 0:
            sigma = np.sqrt(var) * 10 ** (-self._snr / 20)
            noise = np.random.normal(loc=0.0, scale=sigma, size=self.config.timeline.shape)
            return Signal(signal_in.signal + noise)
        else:
            return signal_in


class BandPassFilterBlock(Block):
    def __init__(self, config, bot_freq=1, top_freq=10, name="Band Pass Filter"):
        self.low_freq = bot_freq
        self.hi_freq = top_freq
        super().__init__(config, name)
        self.__name = "BandPass Filter (%d - %d)" % (self.low_freq, self.hi_freq)

    def process(self, signal_in):
        pass

# bandwidth of PM signal = 2 * (<max_freq_deviation>+<max_modulator_freq>)
# max_freq_deviation = np.max(mod_ampl*np.diff(signal)
# hi_freq = <carrier_freq> + BW/2
# low_freq = <carrier_freq> - BW/2


class PhaseDemodulatorBlock(Block):
    def __init__(self, config, name="Phase Demodulator"):
        super().__init__(config, name)

    def process(self, signal_in):

        square_signal = signal_in(signal_in > 0.5)