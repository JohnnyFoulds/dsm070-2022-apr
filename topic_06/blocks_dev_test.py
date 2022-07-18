"""
This module implements the tests created as the block functionality is
implemented to verify correctness.
"""

import unittest
from blocks import Block, UserState, mine_block
from transactions import Transaction, create_signed_transaction


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
