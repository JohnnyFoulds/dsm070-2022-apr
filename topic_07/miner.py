import time
from typing import List

from pykka import ThreadingActor

from blocks import mine_block
from node import NodeStateSummary
from transactions import Transaction
import random


class Miner(ThreadingActor):
    def __init__(self, node, address):
        super().__init__()
        self.node = node
        self.address = address

    def get_address(self):
        if random.uniform(0, 1) < 0.3:
            return bytes.fromhex('bcf177e59d90d6c647918a0882c672be8b1fe289')
        elif random.uniform(0, 1) < 0.5:
            return b's\\s\x884u\x19\x11m\xad\xedA\x8c\x8f\xe5\x84k^]m'
        else:
            return bytes.fromhex('501ace0000000000000000000000000000000000')

        # if random.uniform(0, 1) < 0.2:
        #     return bytes.fromhex('bcf177e59d90d6c647918a0882c672be8b1fe289')
        # elif random.uniform(0, 1) < 0.5:
        #     return b's\\s\x884u\x19\x11m\xad\xedA\x8c\x8f\xe5\x84k^]m'
        # elif random.uniform(0, 1) < 0.1:
        #     return bytes.fromhex('83f78ddd9ba8c7bdfe9dce10d88d7e3aa3f9dc8f')
        # elif random.uniform(0, 1) < 0.1:
        #     return bytes.fromhex('19427d686c5c70f98f24dd487ab32dc3dc015a15')
        # else:
        #     return bytes.fromhex('501ace0000000000000000000000000000000000')

    def mine_block(self):
        print("About to mine block")
        while True:
            summary: NodeStateSummary = self.node.state_summary().get()
            time.sleep(30)
            difficulty = self.node.current_difficulty().get()
            transactions: List[Transaction] = self.node.get_transactions().get()
            transactions.sort(key=lambda t: t.fee, reverse=True)
            transactions = transactions[:25]

            print("Attempting mining with difficulty", difficulty)
            block = mine_block(
                summary.block_id or bytes(32),
                summary.height,
                self.get_address(),
                transactions,
                int(time.time()),
                difficulty,
                time.time() + 15.0
            )
            if block is not None:
                break

        print("Mined block", block.block_id.hex())
        self.node.received_blocks([block])

        if block.nonce != 0:
            time.sleep(87)
            #time.sleep(120)


    def start_mining(self):
        while True:
            self.mine_block()