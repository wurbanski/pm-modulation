import numpy as np
from blocks import Block

__author__ = 'Wojciech Urbański'


class SystemConfiguration():
    blocks = []

    def __init__(self, time=1, sample_rate=1):
        self.timeline = np.arange(0, time, 1 / sample_rate)
        self.time = time
        self.sample_rate = sample_rate

    def add_block(self, block, position=-1):
        if isinstance(block, Block):
            if -1 > position:
                self.blocks.insert(position, block)
            else:
                self.blocks.append(block)
        else:
            raise TypeError("Specified element is not of 'Block' type")

    def list_blocks(self):
        print("Total blocks: ", len(self.blocks))
        for block in self.blocks:
            print("Block ", self.blocks.index(block), ': ', block.name, sep='')

    def refresh_blocks(self):
        for i in range(1, len(self.blocks)):
            print(i - 1, self.blocks[i - 1].name, 'to', i, self.blocks[i].name)
            self.blocks[i].connect(self.blocks[i - 1])

    def get_block(self, i):
        """
        Gets block with specified index number from the system.

        :rtype : Block
        """
        if not isinstance(i, int):
            raise TypeError("Indices can only be integers.")
        if i < len(self.blocks):
            return self.blocks[i]
        else:
            raise ValueError("No block of specified type exists.")

    @property
    def input_block(self):
        return self.blocks[0]

    @property
    def output_block(self):
        return self.blocks[-1]