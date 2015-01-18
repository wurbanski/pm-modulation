import numpy as np
from scipy.signal import lfilter, hilbert

from filters import butter_lowpass, butter_bandpass
from signals import Signal


__author__ = 'Wojciech Urbański'


class Block():
    def __init__(self, config, name="Postawowy blok"):
        self._config = config
        self._input = Signal(np.zeros(self._config.timeline.shape), config.sample_frequency)
        self._output = self._process()
        self._name = name

    def connect(self, previous_block):
        if isinstance(previous_block, Block):
            self._input = previous_block.output
            self._output = self._process()
        else:
            raise TypeError("Nieprawidłowy typ, nie można połączyć")

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
    def __init__(self, config, frequency=1, name="Generator sinusoidalny"):
        self.frequency = frequency
        super().__init__(config, name)

    def _process(self):
        return Signal(np.sin(2 * np.pi * self.frequency * self._config.timeline), self._config.sample_frequency)

    def connect(self, previous_block):
        pass


class PhaseModulatorBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, deviation=1, name="Modulator fazowy"):
        self.frequency = frequency
        self.amplitude = amplitude
        self.deviation = deviation
        super().__init__(config, name)

    def _process(self):
        return Signal(self.amplitude * np.sin(2 * np.pi * self.frequency * self._config.timeline +
                                              self.deviation * self.input.signal), self._config.sample_frequency)


class AWGNChannelBlock(Block):
    def __init__(self, config, snr=20, name="Kanał AWGN"):
        self._snr = snr
        self._noise = np.zeros(config.timeline.shape)
        super().__init__(config, name)

    def _process(self):
        var = self.input.get_energy()
        if var > 0:
            sigma = np.sqrt(var) * 10 ** (-self._snr / 20)
            noise = np.random.normal(loc=0.0, scale=sigma, size=self._config.timeline.shape)
            self._noise = Signal(noise, self._config.sample_frequency)
            return Signal(self.input.signal + noise, self._config.sample_frequency)
        else:
            self._noise = Signal(np.zeros(self._config.timeline.shape), self._config.sample_frequency)
            return self.input

    def get_snr(self):
        mean = np.mean(self.input.signal)
        signal_pwr = np.sum((self.input.signal - mean) ** 2)
        noise_pwr = np.sum(self._noise.signal ** 2)
        return 10 * np.log10(signal_pwr / noise_pwr)


class LowPassFilterBlock(Block):
    def __init__(self, config, high_freq=10, name="Filtr dolprzepustowy"):
        self.high_freq = high_freq
        super().__init__(config, name)
        self._name = "Filtr dolnoprzepustowy (0 - %.2f Hz)" % self.high_freq

    def _process(self):
        b, a = butter_lowpass(self.high_freq, self._config.sample_frequency, analog=False)
        y = lfilter(b, a, self.input.signal)
        return Signal(10e10 * y, self._config.sample_frequency)


class PhaseDemodulatorBlock(Block):
    def __init__(self, config, deviation=1, carrier_freq=1, name="Demodulator fazowy"):
        self._carrier_freq = carrier_freq
        self._deviation = deviation
        super().__init__(config, name)

    def _process(self):
        # Create analytic signal using Hilbert transform
        # Using hilbert twice changes signal to -signal
        h_signal = -hilbert(hilbert(self.input.signal).imag)
        # Angle of analytic signal corresponds to phase of given signal
        phase = np.unwrap(np.angle(h_signal))
        # We reduce the phase value by linear component omega*t
        output = (phase - 2 * np.pi * self._carrier_freq * self._config.timeline) / self._deviation
        # unwrap() sometimes changes first few samples by too much, substracting mean() fixes this
        output -= np.mean(output)
        # output = detrend(phase)
        return Signal(output, self._config.sample_frequency)
