from blocks import SineInputBlock, PhaseModulatorBlock, AWGNChannelBlock, LowPassFilterBlock, PhaseDemodulatorBlock
from system import SystemConfiguration
import matplotlib.pyplot as plt
import numpy as np

__author__ = 'Wojciech Urbański'


modulator_freq = 50
phase_deviation = 0.5
carrier_frequency = 100
carrier_amplitude = 1
sample_freq = 1000
simulation_time = 2

print("Setting up the system...")
config = SystemConfiguration(simulation_time, sample_freq)
print('Timeline shape=', config.timeline.shape)

input_block = SineInputBlock(config, modulator_freq)
print(input_block.name)

config.add_block(input_block)

pm_block = PhaseModulatorBlock(config, carrier_frequency, carrier_amplitude, phase_deviation)
print(pm_block.name)

config.add_block(pm_block)

awgn_block = AWGNChannelBlock(config, snr=30)
print(awgn_block.name)

config.add_block(awgn_block)

BW = 2 * (carrier_frequency + np.max(phase_deviation * np.diff(input_block.output.signal)))
print('Bandwidth of the signal: ', BW)

lpf_block1 = LowPassFilterBlock(config, high_freq=modulator_freq)

pmdemod_block = PhaseDemodulatorBlock(config, carrier_freq=carrier_frequency, deviation=phase_deviation)
config.add_block(pmdemod_block)

lpf_block = LowPassFilterBlock(config, high_freq=BW / 3)
# config.add_block(lpf_block)
config.add_block(lpf_block1)

config.connect_blocks()
# print("phase of input:\n", carrier_frequency*config.timeline[:9] + phase_deviation * modulator_freq * config.timeline[:9])
# print("Phase of modulator:\n", phase_deviation * modulator_freq * config.timeline[:9])
plt.plot(*config.blocks[0].output.plot(), label="Modulator")
plt.plot(*config.blocks[1].output.plot(), label="Modulowany")
plt.legend()
plt.show()
plt.close()

print("Plotting output...")
print("Phase deviation:", phase_deviation)
print("Modulator mean:", np.mean(config.blocks[0].output.signal))
print("Output mean:", np.mean(config.blocks[-1].output.signal))
# config.blocks[0].output.plot(config.timeline, "Modulator")
plt.plot(*config.blocks[-1].input.plot(), label="input")
plt.plot(*config.blocks[-1].output.plot(), label="Output")
plt.legend()
plt.show()
plt.close()

print("...done")
# freqplot(config.blocks[1].output.get_fft(), config.sample_rate)
# plt.hold(True)
# freqplot(config.blocks[-1].output.get_fft(), config.sample_rate)
# plt.show()
# plt.close()


