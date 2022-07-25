"""
This module implements a wrapper around the Zimcoin OpenCL miner
to allow it to be exposed as a method in the block class.
"""

# This method is a wrapper function around the miner in the Miner class.
def mine_block(previous : bytes, height : int, miner : bytes,
               transactions : list, timestamp : int,
               difficulty : int,
               platform_id : int = 0, device_id : int = 0,
               window_size : int = 1e6):
    """
    Mine a block.

    Parameters:
        previous (bytes): The block id of the previous block.
        height (int): The block height.
        miner (bytes): The public key hash of the miner of the block.
        transactions (list): The list of transactions in the block.
        timestamp (int): The unix timestamp of the block.
        difficulty (int): The difficulty of the block.
        platform_id (int): The OpenCL platform id of the miner.
        device_id (int): The OpenCL device id of the miner.
        window_size (int): The window size of the miner.

    Returns:
        Block: The mined block.
    """
    from zimcoin_miner import ZimcoinMiner

    # create a miner
    zimcoin_miner = ZimcoinMiner(
        platform_id=platform_id,
        device_id=device_id,
        window_size=window_size)

    # mine the block and return it
    return zimcoin_miner.mine(
        previous=previous,
        height=height,
        miner=miner,
        transactions=transactions,
        timestamp=timestamp,
        difficulty=difficulty)
