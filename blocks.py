import numpy as np
from scipy.signal import lfilter, butter

from signals import Signal


__author__ = 'Wojciech Urbański'


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


class Block():
    def __init__(self, config, name="Generic Block"):
        self._config = config
        self._signal_in = Signal(np.zeros(self._config.timeline.shape))
        self._signal_out = self.process(self._signal_in)
        self._name = name

    def connect(self, previous_block):
        if isinstance(previous_block, Block):
            self._signal_in = previous_block.output
            self._signal_out = self.process(self._signal_in)
        else:
            raise TypeError("Wrong type, cannot connect.")

    def process(self, signal_in):
        pass

    @property
    def input(self):
        """

        :rtype : Signal
        """
        return self._signal_in

    @property
    def output(self):
        """

        :rtype : Signal
        """
        return self._signal_out

    @property
    def name(self):
        return self._name


class SineInputBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, name="Sine Input"):
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config, name)

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self._config.timeline * self.frequency))


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, name="Phase Modulator"):
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config, name)

    def process(self, signal_in):
        return Signal(self.amplitude * np.sin(self.frequency * self._config.timeline + signal_in.signal))


class AWGNChannelBlock(Block):
    def __init__(self, config, snr=20, name="AWGN Channel"):
        self._snr = snr
        super().__init__(config, name)

    def process(self, signal_in):
        var = signal_in.get_energy()
        if var > 0:
            sigma = np.sqrt(var) * 10 ** (-self._snr / 20)
            noise = np.random.normal(loc=0.0, scale=sigma, size=self._config.timeline.shape)
            return Signal(signal_in.signal + noise)
        else:
            return signal_in


class LowPassFilterBlock(Block):
    def __init__(self, config, high_freq=10, name="Low-Pass Filter"):
        self.high_freq = high_freq
        super().__init__(config, name)
        self._name = "Low-Pass Filter (0 - %d Hz)" % self.high_freq

    def process(self, signal_in):
        b, a = butter_lowpass(self.high_freq, self._config.sample_rate)
        y = lfilter(b, a, self.input.signal)
        return Signal(y)


class PhaseDemodulatorBlock(Block):
    def __init__(self, config, name="Phase Demodulator"):
        super().__init__(config, name)

    def process(self, signal_in):
        square_signal = signal_in(signal_in > 0.5)