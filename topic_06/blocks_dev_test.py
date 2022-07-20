"""
This module implements the tests created as the block functionality is
implemented to verify correctness.
"""

import unittest
import binascii
import hashlib
from blocks import Block, UserState
from transactions import Transaction, create_signed_transaction
from miner import mine_block


class BlockDevelopment(unittest.TestCase):
    """
    Development time test cases.
    """
    def get_test_first_block(self):
        """
        Get a block representing the first in a chain for testing.
        """
        return Block(
                bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
                0,
                bytes.fromhex('4f3ea27a7af06cbe53911d4fb9326730d435255a'),
                [],
                1626626569,
                100000,
                bytes.fromhex('0000193f7397d8ed1a4991d91f8b8d2e55eb56915e884d435de7bbf0b183f335'),
                55419)

    def get_transactions_block(self):
        """
        Get a block with transactions for testing.
        """
        return Block(
                bytes.fromhex('0000193f7397d8ed1a4991d91f8b8d2e55eb56915e884d435de7bbf0b183f335'),
                1,
                bytes.fromhex('4f3ea27a7af06cbe53911d4fb9326730d435255a'),
                [
                    Transaction(
                        bytes.fromhex("9e09208d54c012c0844cf17cfbb175157516dc90"),
                        bytes.fromhex("4f3ea27a7af06cbe53911d4fb9326730d435255a"),
                        bytes.fromhex("3056301006072a8648ce3d020106052b8104000a034200041a719dc420fdbdeef447e90a6368b9486d4afbacd900f6d9d5f62692dfa9ecb695999af4fcf61bdc523021b3aef2b84344b7c4ba7d3a36efe2e5f3eff50e8c54"),
                        390,
                        5,
                        1,
                        bytes.fromhex("3045022100fae9ab97090f2f0fb5715497e12a06438cbccc610bae2f9c019dfa5bdb40f0090220283f5498f22e17ac9ecf4c239d864811dd47cb0ccb8c3584794791fd171e6b90"),
                        bytes.fromhex("0cfd04ed0b2b279c12412687c770b1224c8bfed453292652694339ddade4d63a")),
                ],
                1626626571,
                100000,
                bytes.fromhex('000071f1c701e06e5b91adb4289d6c5227b614bd4441748923826e5d0e8828da'),
                83651)

    def test_block_id(self):
        """
        Verify that a block id is calculated correctly.
        """
        # get the blocks to use for testing
        first_block = self.get_test_first_block()
        transactions_block = self.get_transactions_block()

        # verify the first block_id
        self.assertEqual(
            first_block.block_id,
            first_block.calculate_block_id(),
            'The block id for the first block should be the same as calculated.')

        # verify the second block_id
        self.assertEqual(
            transactions_block.block_id,
            transactions_block.calculate_block_id(),
            'The block id for the second block should be the same as calculated.')

    def test_block_difficulty(self):
        """
        Simple test to verify that the block difficulty is calculated correctly.
        """
        # get the blocks to use for testing
        first_block = self.get_test_first_block()
        second_block = self.get_transactions_block()

        # verify the first block difficulty
        target = 2 ** 256 // first_block.difficulty
        self.assertLess(
            int.from_bytes(first_block.block_id, byteorder='big'),
            target)

        self.assertTrue(
            first_block.verify_proof_of_work(),
            'The first block should have a valid proof of work.')

        # verify the second block difficulty
        self.assertTrue(
            second_block.verify_proof_of_work(),
            'The second block should have a valid proof of work.')

        # test with an invalid nonce
        first_block.nonce = 0
        first_block.block_id = first_block.calculate_block_id()

        self.assertFalse(
            first_block.verify_proof_of_work(),
            'The first block should have an invalid proof of work.')

    def test_understand_digest_update(self):
        """
        Understand how the SHA256 digest update works.
        """
        first_string = "hello"
        second_string = "world"

        # do the hash in one go
        complete_hash = hashlib.sha256()
        complete_hash.update((first_string + second_string).encode('utf-8'))
        complete_hash = complete_hash.digest()

        # do the hash in steps with update
        partial_hash = hashlib.sha256()
        partial_hash.update(first_string.encode('utf-8'))
        partial_hash.update(second_string.encode('utf-8'))
        partial_hash = partial_hash.digest()

        self.assertEqual(complete_hash, partial_hash)

    def test_nonce_value(self):
        """
        Test the mechanism to try out different nonce values. This will
        be important to understand when implementing the mine function.
        """
        # get the block for testing
        block = self.get_transactions_block()
        #print(binascii.hexlify(block.block_id))

        # build the byte array without the nonce
        block_bytes = block.to_bytes()

        # get the byte array of the valid nonce
        nonce_bytes = block.nonce.to_bytes(8, byteorder='little', signed=False)
        print(nonce_bytes)

        # get the hash digest of the combined byte arrays that should match
        # the block_id
        block_id = hashlib.sha256()
        block_id.update(block_bytes + nonce_bytes)

        self.assertEqual(
            block_id.digest(),
            block.block_id,
        )

        #print(binascii.hexlify(block_id.digest()))

    def test_difficulty(self):
        """
        Ensure that the difficulty is verified correctly.
        """
        test_block = self.get_test_first_block()

        # verify with the same difficulty
        test_block.verify_and_get_changes(
            difficulty=test_block.difficulty,
            previous_user_states=dict())

        # verify with a higher difficulty
        with self.assertRaisesRegex(Exception, 'Difficulty value not valid'):
            test_block.verify_and_get_changes(
                difficulty=test_block.difficulty + 1,
                previous_user_states=dict())

    def test_block_valid_id(self):
        """
        Ensure that the the block_id is verified correctly,
        """
        # get tehe blocks for testing
        first_block = self.get_test_first_block()
        second_block = self.get_transactions_block()

        # the first block should be valid
        first_block.verify_and_get_changes(
            difficulty=first_block.difficulty,
            previous_user_states=dict())

        # test with an invalid block id
        first_block.block_id = second_block.block_id
        with self.assertRaisesRegex(Exception, 'Invalid block id'):
            first_block.verify_and_get_changes(
                difficulty=first_block.difficulty,
                previous_user_states=dict())

    def test_transaction_count(self):
        """
        Ensure that the transaction count is verified correctly.
        """
        # get the block for testing
        test_block = self.get_transactions_block()

        test_transaction = test_block.transactions[0]
        test_states = dict([(test_transaction.sender_hash, UserState(1000, 0))])

        # the first block should be valid
        test_block.verify_and_get_changes(
            difficulty=test_block.difficulty,
            previous_user_states=test_states)

        # test with to many transactions
        test_transaction = test_block.transactions[0]
        for i in range(0, 26):
            test_block.transactions.append(test_transaction)

        test_block = mine_block(
            test_block.previous,
            test_block.height,
            test_block.miner,
            test_block.transactions,
            test_block.timestamp,
            difficulty=100,
            window_size=1e4)

        with self.assertRaisesRegex(Exception, 'Too many transactions in block'):
            test_block.verify_and_get_changes(
                difficulty=test_block.difficulty,
                previous_user_states=dict())

    def test_miner_address(self):
        """
        Ensure that the miner address is verified correctly.
        """
        # get the block for testing
        test_block = self.get_transactions_block()

        test_transaction = test_block.transactions[0]
        test_states = dict([(test_transaction.sender_hash, UserState(1000, 0))])

        # the first block should be valid
        test_block.verify_and_get_changes(
            difficulty=test_block.difficulty,
            previous_user_states=test_states)

        # test with an invalid miner address
        test_block.miner = b'test'
        test_block = mine_block(
            test_block.previous,
            test_block.height,
            test_block.miner,
            test_block.transactions,
            test_block.timestamp,
            difficulty=100,
            window_size=1e4)

        with self.assertRaisesRegex(Exception, 'Invalid miner address'):
            test_block.verify_and_get_changes(
                difficulty=test_block.difficulty,
                previous_user_states=test_states)
