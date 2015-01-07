from blocks import SineInputBlock, PhaseModulatorBlock, AWGNChannelBlock, LowPassFilterBlock, PhaseDemodulatorBlock, \
    Block
from system import SystemConfiguration

__author__ = 'Wojciech Urbański'

import signals
from signals import freqplot
import matplotlib.pyplot as plt
import numpy as np


print("Setting up the system...")
config = SystemConfiguration(2, 500)
print('Timeline shape=', config.timeline.shape)

print("Setting up InputBlock...")
modulator_freq = 50
modulator_amplitude = 2
input_block = SineInputBlock(config, modulator_freq, modulator_amplitude)
print(input_block.name)

print("Adding block to the system...")
config.add_block(input_block)

print("Setting up PhaseModulatorBlock")
carrier_frequency = 100
carrier_amplitude = 5
pm_block = PhaseModulatorBlock(config, carrier_frequency, carrier_amplitude)
print(pm_block.name)

print("Adding block to the system...")
config.add_block(pm_block)

print("Setting up AWGNChannelBlock")
awgn_block = AWGNChannelBlock(config, snr=20)
print(awgn_block.name)

print("Adding block to the system...")
config.add_block(awgn_block)

print("Adding LowPassFilter to the system...")
BW = 2 * (input_block.frequency + np.max(input_block.amplitude * np.diff(input_block.output.signal)))
print('Bandwidth of the signal: ', BW)
lpf_block1 = LowPassFilterBlock(config, high_freq=BW)
config.add_block(lpf_block1)
pmdemod_block = PhaseDemodulatorBlock(config, carrier_frequency)
config.add_block(pmdemod_block)
lpf_block = LowPassFilterBlock(config, high_freq=1.8 * modulator_freq)
print(lpf_block.name)
config.add_block(lpf_block)
print("Listing blocks...")
config.list_blocks()

print("Connecting Blocks...")
# pm_block.input(input_block)
config.refresh_blocks()

config.blocks[0].output.plot(config.timeline, "Modulator")
config.blocks[1].output.plot(config.timeline, "Modulowany")
plt.legend()
plt.show()
plt.close()

print("Plotting output...")
config.blocks[0].output.plot(config.timeline, "Modulator")
config.blocks[-1].input.plot(config.timeline, "Input")
config.blocks[-1].output.plot(config.timeline, "Output")
plt.legend()
plt.show()
plt.close()

print("...done")
# freqplot(config.blocks[1].output.get_fft(), config.sample_rate)
# plt.hold(True)
# freqplot(config.blocks[-1].output.get_fft(), config.sample_rate)
# plt.show()
# plt.close()


