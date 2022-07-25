import unittest
from time import time

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import ec

from blockchain_state import BlockchainState, verify_reorg
from blocks import mine_block
from transactions import create_signed_transaction


def calculate_sha1_hash(public_key):
    digest = hashes.Hash(hashes.SHA1())
    digest.update(public_key)
    return digest.finalize()


def private_key_to_public_key(private_key):
    return private_key.public_key().public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)


ALICE_KEY = ec.generate_private_key(ec.SECP256K1)
ALICE_ADDRESS = calculate_sha1_hash(private_key_to_public_key(ALICE_KEY))

BOB_KEY = ec.generate_private_key(ec.SECP256K1)
BOB_ADDRESS = calculate_sha1_hash(private_key_to_public_key(BOB_KEY))


class BlockchainStateTest(unittest.TestCase):
    def test_difficulty_calculation(self):
        state = BlockchainState([], dict(), 0)
        previous = bytes([0] * 32)
        for height, (timestamp, difficulty) in enumerate([
            (0, 1000), (34, 1000), (60, 1000), (60, 1000), (100, 1000), (500, 1000), (600, 1000), (800, 1000),
            (805, 1000), (805, 1000), (900, 1000), (1500, 1320), (1600, 840)]):
            block = mine_block(previous, height, ALICE_ADDRESS, [], timestamp, difficulty, time() + 100)
            state.verify_and_apply_block(block)
            previous = block.block_id

        block = mine_block(previous, 13, ALICE_ADDRESS, [], 1600, 840, time() + 100)
        with self.assertRaisesRegex(Exception, "Incorrect difficulty"):
            state.verify_and_apply_block(block)

    def test_undo(self):
        state = BlockchainState([], dict(), 0)
        previous = bytes([0] * 32)
        total_difficulty = 0
        for height in range(15):
            block = mine_block(previous, height, ALICE_ADDRESS, [], 120 * height, state.calculate_difficulty(),
                               time() + 100)
            state.verify_and_apply_block(block)
            total_difficulty += block.difficulty
            previous = block.block_id

        transactions = [create_signed_transaction(ALICE_KEY, BOB_ADDRESS, 3000, 25, 0)]
        block = mine_block(previous, 15, BOB_ADDRESS, transactions, 120 * 15, state.calculate_difficulty(),
                           time() + 150)
        state.verify_and_apply_block(block)
        total_difficulty += block.difficulty
        previous = block.block_id

        transactions = [
            create_signed_transaction(BOB_KEY, ALICE_ADDRESS, 1000, 50, 0),
            create_signed_transaction(ALICE_KEY, BOB_ADDRESS, 100, 50, 1)]
        block = mine_block(previous, 16, BOB_ADDRESS, transactions, 120 * 16, state.calculate_difficulty(),
                           time() + 150)
        state.verify_and_apply_block(block)
        previous = block.block_id

        block = mine_block(previous, 17, BOB_ADDRESS, [], 120 * 17, state.calculate_difficulty(), time() + 150)
        state.verify_and_apply_block(block)
        previous = block.block_id

        assert len(state.longest_chain) == 18
        assert state.user_states[ALICE_ADDRESS].balance == 147_850
        assert state.user_states[ALICE_ADDRESS].nonce == 1
        assert state.user_states[BOB_ADDRESS].balance == 32_150
        assert state.user_states[BOB_ADDRESS].nonce == 0

        state.undo_last_block()
        state.undo_last_block()

        assert len(state.longest_chain) == 16
        assert state.user_states[ALICE_ADDRESS].balance == 147_000
        assert state.user_states[ALICE_ADDRESS].nonce == 0
        assert state.user_states[BOB_ADDRESS].balance == 13_000
        assert state.user_states[BOB_ADDRESS].nonce == -1
        assert state.total_difficulty == total_difficulty

    def test_previous_validation(self):
        state = BlockchainState([], dict(), 0)
        block = mine_block(bytes([1] * 32), 0, ALICE_ADDRESS, [], 0, 1000, time() + 150)

        with self.assertRaisesRegex(Exception, "previous block id"):
            state.verify_and_apply_block(block)

        block = mine_block(bytes([0] * 32), 0, ALICE_ADDRESS, [], 0, 1000, time() + 150)
        state.verify_and_apply_block(block)

        block = mine_block(bytes([0] * 32), 1, ALICE_ADDRESS, [], 0, 1000, time() + 150)
        with self.assertRaisesRegex(Exception, "previous block id"):
            state.verify_and_apply_block(block)

        block = mine_block(bytes([1] * 32), 1, ALICE_ADDRESS, [], 0, 1000, time() + 150)
        with self.assertRaisesRegex(Exception, "previous block id"):
            state.verify_and_apply_block(block)

    def test_difficulty_with_zero_time(self):
        state = BlockchainState([], dict(), 0)
        previous = bytes([0] * 32)
        for height in range(11):
            block = mine_block(previous, height, ALICE_ADDRESS, [], 0, 1000, time() + 100)
            state.verify_and_apply_block(block)
            previous = block.block_id

        assert state.calculate_difficulty() == 1_200_000

    def test_reorg(self):
        state = BlockchainState([], dict(), 0)
        previous = bytes([0] * 32)
        for height in range(15):
            block = mine_block(previous, height, ALICE_ADDRESS, [], 120 * height, state.calculate_difficulty(),
                               time() + 100)
            state.verify_and_apply_block(block)
            previous = block.block_id

        previous = state.longest_chain[7].block_id
        blocks = []
        for height in range(8, 15):
            block = mine_block(previous, height, BOB_ADDRESS, [], 120 * height, state.longest_chain[height].difficulty,
                               time() + 100)
            blocks.append(block)
            previous = block.block_id

        with self.assertRaisesRegex(Exception, "total difficulty"):
            verify_reorg(state, blocks)

        assert state.user_states[ALICE_ADDRESS].balance == 150_000
        assert BOB_ADDRESS not in state.user_states

        block = mine_block(previous, 15, BOB_ADDRESS, [], 120 * 15, state.calculate_difficulty(), time() + 100)
        blocks.append(block)
        new_state = verify_reorg(state, blocks)

        assert state.user_states[ALICE_ADDRESS].balance == 150_000
        assert BOB_ADDRESS not in state.user_states

        assert new_state.user_states[ALICE_ADDRESS].balance == 80_000
        assert new_state.user_states[BOB_ADDRESS].balance == 80_000


if __name__ == '__main__':
    unittest.main(exit=False)
