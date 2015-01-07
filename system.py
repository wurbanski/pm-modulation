import numpy as np
from blocks import Block

__author__ = 'Wojciech Urbański'


class SystemConfiguration():
    blocks = []

    def __init__(self, time=1, sample_rate=1):
        self.timeline = np.arange(0, time, 1 / sample_rate)
        self.time = time
        self.sample_rate = sample_rate

    def __iter__(self):
        return self.blocks.__iter__()

    def add_block(self, block, position=-1):
        if not isinstance(block, Block):
            raise TypeError("Specified element is not of 'Block' type")
        if -1 > position:
            self.blocks.insert(position, block)
        else:
            self.blocks.append(block)

    def list_blocks(self):
        print("Total blocks: ", len(self.blocks))
        for i, block in enumerate(self.blocks):
            print("%2d: %s" % (i, block.name))

    def refresh_blocks(self):
        for i in range(1, len(self.blocks)):
            print("%d %s - %d %s" % (i - 1, self.blocks[i - 1].name, i, self.blocks[i].name))
            self.blocks[i].connect(self.blocks[i - 1])

    def get_block(self, i):
        """
        Gets block with specified index number from the system.

        :rtype : Block
        """
        try:
            return self.blocks[i]
        except IndexError:
            return None
        except TypeError:
            return None

    @property
    def input_block(self):
        return self.blocks[0]

    @property
    def output_block(self):
        return self.blocks[-1]