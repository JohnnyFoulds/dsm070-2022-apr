"""
This module implements the functionality to keep track of the longest
chain of blocks.
"""

import logging
from copy import deepcopy
from blocks import Block


class BlockchainState:
    """
    This class will be used to keep track of the state of the blockchain.
    """
    def __init__(self,
                 longest_chain : list,
                 user_states : dict,
                 total_difficulty : int):
        """
        Initialize the blockchain state.

        Parameters:
            longest_chain (list): The longest chain of blocks.
            user_states (dict): A dictionary of user states.
            total_difficulty (int): The total difficulty of the chain.
        """
        self.longest_chain = longest_chain
        self.user_states = user_states
        self.total_difficulty = total_difficulty

    def calculate_difficulty(self) -> int:
        """
        Calculate the difficulty of the chain.

        Returns:
            int: The difficulty of the chain.
        """
        total_difficulty = 1000

        if len(self.longest_chain) > 10:
            total_difficulty_for_period = 0

            # calculate the difficulty for the last 10 blocks
            blocks = self.longest_chain[-10:]
            for block in blocks:
                total_difficulty_for_period += block.difficulty

            # calculate the total time for the period
            total_time_for_period = \
                  self.longest_chain[-1].timestamp \
                - self.longest_chain[-11].timestamp

            # handle the case where the period is too short
            if total_time_for_period == 0:
                logging.warning(f'Period is too short: {total_time_for_period}')
                total_time_for_period = 1

            # calculate the difficulty for the period
            total_difficulty = \
                (total_difficulty_for_period // total_time_for_period) * 120

        return total_difficulty

    def verify_and_apply_block(self, block : Block) -> bool:
        """
        Verify and apply a block to the blockchain state.

        Parameters:
            block (Block): The block to verify and apply.

        Returns:
            bool: True if the block was verified and applied, False otherwise.
        """
        # verify the block height
        assert block.height == len(self.longest_chain), 'Block height is wrong'

        # verify the previous block id
        if len(self.longest_chain) == 0:
            assert block.previous == bytes([0] * 32), \
                'previous block id is wrong'
        else:
            assert block.previous == self.longest_chain[-1].block_id, \
                'previous block id is wrong'

        # verify the timestamp
        if len(self.longest_chain) > 0:
            assert block.timestamp >= self.longest_chain[-1].timestamp, \
                'Timestamp is wrong'

        # verify the block with the current difficulty
        self.user_states = block.verify_and_get_changes(
            self.calculate_difficulty(),
            self.user_states)

        # add the block to the longest chain
        self.total_difficulty = self.calculate_difficulty()
        self.longest_chain.append(block)

verify_reorg = None
