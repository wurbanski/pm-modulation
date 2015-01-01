__author__ = 'Wojciech Urbański'

import devices
from devices import freqplot
import matplotlib.pyplot as plt
import numpy as np

print("Setting up the system...")
config = devices.SystemConfiguration(1, 500)

print("Setting up InputBlock...")
input_block = devices.SineInputBlock(config, 10, 50)
print(input_block.name)

print("Adding block to the system...")
config.add_block(input_block)

print("Setting up PhaseModulatorBlock")
pm_block = devices.PhaseModulatorBlock(config, 1, 10)
print(pm_block.name)

print("Adding block to the system...")
config.add_block(pm_block)

print("Setting up AWGNChannelBlock")
awgn_block = devices.AWGNChannelBlock(config)
print(awgn_block.name)

print("Adding block to the system...")
config.add_block(awgn_block)

print("Adding LowPassFilter to the system...")
BW = 2 * (input_block.frequency + np.max(input_block.amplitude * np.diff(input_block.output.signal)))
print('Bandwidth of the signal: ', BW)
lpf_block = devices.LowPassFilterBlock(config, high_freq=BW)
print(lpf_block.name)
config.add_block(lpf_block)

print("Listing blocks...")
config.list_blocks()

print("Connecting Blocks...")
# pm_block.input(input_block)
config.refresh_blocks()

print("Plotting input...")
plt.plot(config.blocks[0].output.signal)
plt.show()
plt.close()
print("...done")
config.get_block(1).input.plot(config.timeline)
plt.hold(True)
config.get_block(1).output.plot(config.timeline)
plt.show()
plt.close()
print("Plotting output...")
config.output_block.input.plot(config.timeline, 'Filter: Input signal')
plt.hold(True)
config.output_block.output.plot(config.timeline, 'Filter: Output signal')
config.get_block(1).output.plot(config.timeline, 'Input Signal')
plt.legend()
plt.show()
plt.close()
print("...done")
# freqplot(config.blocks[1].output.get_fft(), config.sample_rate)
# plt.hold(True)
# freqplot(config.blocks[-1].output.get_fft(), config.sample_rate)
# plt.show()
# plt.close()


