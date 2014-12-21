__author__ = 'Wojciech Urbański'

import devices
import matplotlib.pyplot as plt

print("Setting up the system...")
config = devices.SystemConfiguration(1, 100)

print("Setting up InputBlock...")
input_block = devices.SineInputBlock(config, 10, 1)
print(input_block.name())

print("Adding block to the system...")
config.add_block(input_block)

print("Setting up PhaseModulatorBlock")
pm_block = devices.PhaseModulatorBlock(config, 10, 1)
print(pm_block.name())

print("Adding block to the system...")
config.add_block(pm_block)

print("Setting up AWGNChannelBlock")
awgn_block = devices.AWGNChannelBlock(config)
print(awgn_block.name())

print("Adding block to the system...")
config.add_block(awgn_block)

print("Listing blocks...")
config.list_blocks()

print("Connecting Blocks...")
# pm_block.input(input_block)
config.refresh_blocks()

print("Plotting input...")
plt.plot(config.blocks[0].signal_out.signal)
plt.show()
plt.close()
print("...done")
plt.plot(config.blocks[1].signal_in.signal)
plt.hold(True)
plt.plot(config.blocks[1].output().signal)
plt.show()
plt.close()
print("Plotting output...")
plt.plot(config.blocks[-1].output().signal)
plt.show()
plt.close()
print("...done")