import numpy as np
from scipy.signal import lfilter, butter, hilbert
from matplotlib import pyplot as plt
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
        self._input = Signal(np.zeros(self._config.timeline.shape))
        self._output = self._process()
        self._name = name

    def connect(self, previous_block):
        if isinstance(previous_block, Block):
            self._input = previous_block.output
            self._output = self._process()
        else:
            raise TypeError("Wrong type, cannot connect.")

    def _process(self):
        pass

    @property
    def input(self):
        """

        :rtype : Signal
        """
        return self._input

    @property
    def output(self):
        """

        :rtype : Signal
        """
        return self._output

    @property
    def name(self):
        return self._name


class SineInputBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, name="Sine Input"):
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config, name)

    def _process(self):
        return Signal(self.amplitude * np.sin(self._config.timeline * self.frequency))


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, name="Phase Modulator"):
        self.frequency = frequency
        self.amplitude = amplitude
        super().__init__(config, name)

    def _process(self):
        return Signal(self.amplitude * np.sin(self.frequency * self._config.timeline + self.input.signal))


class AWGNChannelBlock(Block):
    def __init__(self, config, snr=20, name="AWGN Channel"):
        self._snr = snr
        self._noise = None
        super().__init__(config, name)

    def _process(self):
        var = self.input.get_energy()
        if var > 0:
            sigma = np.sqrt(var) * 10 ** (-self._snr / 20)
            noise = np.random.normal(loc=0.0, scale=sigma, size=self._config.timeline.shape)
            self._noise = noise
            return Signal(self.input.signal + noise)
        else:
            self._noise = np.zeros(self._config.timeline.shape)
            return self.input


class LowPassFilterBlock(Block):
    def __init__(self, config, high_freq=10, name="Low-Pass Filter"):
        self.high_freq = high_freq
        super().__init__(config, name)
        self._name = "Low-Pass Filter (0 - %d Hz)" % self.high_freq

    def _process(self):
        b, a = butter_lowpass(self.high_freq, self._config.sample_rate)
        y = lfilter(b, a, self.input.signal)
        return Signal(y)


class PhaseDemodulatorBlock(Block):
    def __init__(self, config, carrier_freq=1, name="Phase Demodulator"):
        self._carrier_freq = carrier_freq
        super().__init__(config, name)

    def _process(self):
        h_signal = hilbert(self.input.signal)
        phase = np.unwrap(np.angle(h_signal))
        output = phase - self._carrier_freq * self._config.timeline
        return Signal(output)




