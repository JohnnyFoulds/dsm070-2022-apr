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
                logging.warning('Period is too short: %d', total_time_for_period)
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
        self.total_difficulty += self.calculate_difficulty()
        self.longest_chain.append(block)

    def undo_last_block(self) -> None:
        """
        Undo the last block in the blockchain state.
        """
        # remove the last block from the longest chain
        block = self.longest_chain.pop()

        # update the total difficulty
        self.total_difficulty -= block.difficulty

        # update the user states
        self.user_states = block.get_changes_for_undo(self.user_states)

def verify_reorg(
        old_state : BlockchainState, new_branch : list) -> BlockchainState:
    """
    This function attempts to calculate a new blockchain state
    corresponding to the new longest chain, and raise an exception if
    the new chain is invalid.

    Parameters:
        old_state (BlockchainState): The old blockchain state.
        new_branch (list): The new branch of blocks.

    Returns:
        BlockchainState: The new blockchain state.
    """
    # copy the old state
    new_state = deepcopy(old_state)

    # undo blocks until the height is the same as the first block in
    # the new branch
    while new_state.longest_chain[-1].height >= new_branch[0].height:
        new_state.undo_last_block()

    # add the new blocks to the new state
    for block in new_branch:
        new_state.verify_and_apply_block(block)

    # verify that the new chain is valid
    if new_state.total_difficulty <= old_state.total_difficulty:
        raise Exception('The total difficulty of the new chain is '
                       +'lower than the old chain')

    return new_state
