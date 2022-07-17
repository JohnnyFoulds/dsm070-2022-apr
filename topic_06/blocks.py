"""
This module implements the functionality for a block in the Zimcoin
blockchain.
"""

class Block:
    """
    This class represents a block in the blockchain.
    """
    def __init__(self, previous : bytes, height : int, miner : bytes,
                 transactions : list, timestamp : int, difficulty : int,
                 block_id : bytes, nonce : int):
        """
        Initialize the block.

        Parameters:
            previous (bytes): The block id of the block before this one
                in the block chain. This is zero for the first block.

            height (int): The number of blocks before this one in the
                block chain. The first block will have a height of 0.

            miner (bytes): The public key hash of the user responsible
                for mining this block.

            transactions (list): The list of transactions in the block.

            timestamp (int): The unix timestamp of the block.

            difficulty (int): An integer between 1 and 2**128 - 1
                indicating difficulty of the proof of work needed to
                mine this block.

            block_id (bytes):A 32 byte hash of the block.

            nonce (int): n integer between 0 and 2**64 - 1.
        """
        self.previous = previous
        self.height = height
        self.miner = miner
        self.transactions = transactions
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.block_id = block_id
        self.nonce = nonce

    def verify_and_get_changes(self,
                               difficulty : int,
                               previous_user_states : dict) -> dict:
        """
        Verify that the block is valid and return the changes to the
        user states if the block is valid.

        Parameters:
            difficulty (int): The expected difficulty for this block.

            previous_user_states (dict): A dictionary of user states
                representing the state of the users before the block was
                mined.

        Returns:
            dict: A dictionary of user states representing the state of
                the users after the block was mined.
        """


# This method is a wrapper function around the miner in the Miner class.
def mine_block(previous : bytes, height : int, miner : bytes,
               transactions : list, timestamp : int,
               difficulty : int) -> Block:
    """
    Mine a block.

    Parameters:
        previous (bytes): The block id of the previous block.
        height (int): The block height.
        miner (bytes): The public key hash of the miner of the block.
        transactions (list): The list of transactions in the block.
        timestamp (int): The unix timestamp of the block.
        difficulty (int): The difficulty of the block.

    Returns:
        Block: The mined block.
    """
