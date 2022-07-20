"""
This module implements the functionality for a block in the Zimcoin
blockchain.
"""

from copy import deepcopy
import hashlib

class UserState:
    """
    This class will be used to help keep track of the state of users as
    blocks are accepted onto the blockchain.
    """
    def __init__(self, balance : int, nonce : int):
        """
        Initialize the user state.

        Parameters:
            balance (int): The (on-chain) balance of the user.
            nonce (int): The most recently used nonce of the user.
        """
        self.balance = balance
        self.nonce = nonce

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
        self.block_reward = 10_000

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
        # verify that the difficulty is correct
        assert self.difficulty == difficulty, 'Difficulty value not valid'

        # verify the block id
        block_id = self.calculate_block_id()
        assert self.block_id == block_id, 'Invalid block id'

        # verify that there are at most 25 transactions in the block
        assert len(self.transactions) <= 25, 'Too many transactions in block'

        # verify the miner address
        assert len(self.miner) == 20, 'Invalid miner address'

        # verify that the proof of work is valid
        assert self.verify_proof_of_work(), 'Invalid proof of work'

        # verify that the transactions are valid
        # if self.height == 0:
        #     assert len(self.transactions) == 0, 'There are transactions in the genesis block'

        user_states = self.verify_and_update_transactions(previous_user_states)

        return user_states

    def calculate_block_id(self) -> bytes:
        """
        Calculate the block id

        Returns:
            bytes: A 32 byte hash of the block.
        """
        digest = hashlib.sha256()
        digest.update(self.previous)
        digest.update(self.miner)

        # process the transactions in the block
        for transaction in self.transactions:
            digest.update(transaction.txid)

        digest.update(self.timestamp.to_bytes(8, byteorder='little', signed=False))
        digest.update(self.difficulty.to_bytes(16, byteorder='little', signed=False))
        digest.update(self.nonce.to_bytes(8, byteorder='little', signed=False))

        return digest.digest()

    def to_bytes(self) -> bytes:
        """
        Get a byte array representation of the block without the nonce
        value from which the block_id should be calculated.

        Returns:
            bytes: A byte array representation of the block.
        """
        block_bytes = bytearray()
        block_bytes.extend(self.previous)
        block_bytes.extend(self.miner)

        # process the transactions in the block
        for transaction in self.transactions:
            block_bytes.extend(transaction.txid)

        block_bytes.extend(self.timestamp.to_bytes(8, byteorder='little', signed=False))
        block_bytes.extend(self.difficulty.to_bytes(16, byteorder='little', signed=False))

        return block_bytes

    def calculate_target(self) -> int:
        """
        Calculate the target for the proof of work.

        Returns:
            int: The target for the proof of work.
        """
        return 2 ** 256 // self.difficulty

    def verify_proof_of_work(self) -> bool:
        """
        Verify that the proof of work is valid.

        Returns:
            bool: True if the proof of work is valid, False otherwise.
        """
        # calculate the block id
        block_id = self.calculate_block_id()
        assert self.block_id == block_id, 'Block id value not valid'

        block_id_int = int.from_bytes(block_id, byteorder='big')

        # calculate the target
        target = self.calculate_target()

        # verify that the block id is less than the difficulty
        return block_id_int < target

    def verify_and_update_transactions(self, previous_user_states : dict) -> dict:
        """
        Verify that the transactions in the block are valid.

        Parameters:
            previous_user_states (dict): A dictionary of user states
                representing the state of the users before the block was
                mined.

        Returns:
            bool: True if the transactions are valid, False otherwise.
        """
        # create the output user states
        user_states = deepcopy(previous_user_states)

        # add the miner to the user states
        if self.miner not in user_states:
            user_states[self.miner] = UserState(0, 0)

        # allocate the block reward to the miner
        miner_state = user_states[self.miner]
        miner_state.balance += self.block_reward

        for transaction in self.transactions:
            # get the sender user state
            sender_state = user_states.get(transaction.sender_hash)
            assert sender_state is not None, 'Sender user state not found'

            # verify the transaction
            transaction.verify(
                sender_balance=sender_state.balance,
                sender_previous_nonce=sender_state.nonce)

            # add the receiver to the user states if required
            if transaction.recipient_hash not in user_states:
                user_states[transaction.recipient_hash] = UserState(0, 0)

        return user_states
