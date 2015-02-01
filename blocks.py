import numpy as np
from scipy.signal import lfilter, hilbert, filtfilt

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


class SineGeneratorBlock(Block):
    def __init__(self, config, frequency=1, start_ph=0, name="Generator sinusoidalny"):
        self.frequency = frequency
        self._start_ph = start_ph
        super().__init__(config, name)

    def _process(self):
        return Signal(np.sin(2 * np.pi * self.frequency * self._config.timeline + self._start_ph),
                      self._config.sample_frequency)

    def connect(self, previous_block):
        pass


class PhaseModemBlock(Block):
    def __init__(self, config, frequency=1, amplitude=1, deviation=1, name="Modulator fazowy"):
        self._frequency = frequency
        self._amplitude = amplitude
        self._deviation = deviation
        super().__init__(config, name)


class PhaseModulatorBlock(PhaseModemBlock):
    def _process(self):
        return Signal(self._amplitude * np.sin(2 * np.pi * self._frequency * self._config.timeline +
                                               self._deviation * self.input.signal), self._config.sample_frequency)


class PhaseDemodulatorBlock(PhaseModemBlock):
    def _process(self):
        # Create analytic signal using Hilbert transform
        # Using hilbert twice changes signal to -signal
        h_signal = -hilbert(hilbert(self.input.signal).imag)
        # Angle of analytic signal corresponds to phase of given signal
        phase = np.unwrap(np.angle(h_signal))
        # We reduce the phase value by linear component omega*t
        output = (phase - 2 * np.pi * self._frequency * self._config.timeline) / self._deviation
        # unwrap() sometimes changes first few samples by too much, substracting mean() fixes this
        # output -= np.mean(output)
        return Signal(output, self._config.sample_frequency)


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


class BandPassFilterBlock(Block):
    def __init__(self, config, low_freq=5, high_freq=10, order=5, name="Filtr dolprzepustowy"):
        self._high_freq = high_freq
        self._low_freq = low_freq
        self._order = order
        super().__init__(config, name)
        self._name = "Filtr pasmoprzepustowy (%.2f - %.2f Hz)" % (self._low_freq, self._high_freq)

    def _process(self):
        b, a = butter_bandpass(self._low_freq, self._high_freq, self._config.sample_frequency, order=self._order)
        y = filtfilt(b, a, self.input.signal)
        return Signal(y, self._config.sample_frequency)


class NoiseGeneratorBlock(Block):
    def __init__(self, config, high_freq, name="Generator szumu pasmowego"):
        self._high_freq = high_freq
        super().__init__(config, name)

    def _process(self):
        noise = np.random.normal(loc=0.0, scale=1, size=self._config.timeline.shape)
        b, a = butter_lowpass(self._high_freq, self._config.sample_frequency, order=5)
        y = filtfilt(b, a, noise)
        return Signal(y, self._config.sample_frequency)