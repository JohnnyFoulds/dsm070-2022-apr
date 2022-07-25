"""
This module implements the functionality to keep track of the longest
chain of blocks.
"""

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

        if (len(self.longest_chain) > 10):
            total_difficulty_for_period = 0

            # calculate the difficulty for the last 10 blocks
            blocks = self.longest_chain[-10:]
            for block in blocks:
                total_difficulty_for_period += block.difficulty

            # caluclate the total time for the period
            total_time_for_period = \
                  self.longest_chain[-1].timestamp \
                - self.longest_chain[-11].timestamp

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



verify_reorg = None