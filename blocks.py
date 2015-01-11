import numpy as np
from scipy.signal import lfilter, butter, hilbert, detrend
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
    def __init__(self, config, frequency=1, name="Sine Input"):
        self.frequency = frequency
        super().__init__(config, name)

    def _process(self):
        return Signal(np.sin(self.frequency * self._config.timeline))


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, deviation=1, name="Phase Modulator"):
        self.frequency = frequency
        self.amplitude = amplitude
        self.deviation = deviation
        super().__init__(config, name)

    def _process(self):
        return Signal(self.amplitude * np.sin(self.frequency * self._config.timeline +
                                              self.deviation * self.input.signal))


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
    def __init__(self, config, deviation=1, carrier_freq=1, name="Phase Demodulator"):
        self._carrier_freq = carrier_freq
        self._deviation = deviation
        super().__init__(config, name)

    def _process(self):
        # Create analytic signal using Hilbert transform
        h_signal = hilbert(self.input.signal)
        # Angle of analytic signal corresponds to phase of signal
        phase = np.unwrap(np.angle(h_signal))
        # Hilbert transform changes sine to cosine, hence +pi/2
        output = (phase + np.pi / 2 - self._carrier_freq * self._config.timeline) / self._deviation
        return Signal(output)




