import time
from typing import List

from pykka import ThreadingActor

from blocks import mine_block
from node import NodeStateSummary
from transactions import Transaction


class Miner(ThreadingActor):
    def __init__(self, node, address):
        super().__init__()
        self.node = node
        self.address = address

    def mine_block(self):
        print("About to mine block")
        while True:
            summary: NodeStateSummary = self.node.state_summary().get()
            time.sleep(30)
            difficulty = self.node.current_difficulty().get()
            transactions: List[Transaction] = self.node.get_transactions().get()
            transactions.sort(key=lambda t: t.fee, reverse=True)
            transactions = transactions[:25]

            #time.sleep(30)

            print("Attempting mining with difficulty", difficulty)
            block = mine_block(
                summary.block_id or bytes(32),
                summary.height,
                self.address,
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
            time.sleep(2*60)
            #time.sleep(4*60)

        #time.sleep(76)


    def start_mining(self):
        mine_count = 0
        while True:
            self.mine_block()

            mine_count += 1
            # if mine_count % 3 == 0:
            #     print("*** Mined", mine_count, "blocks. Having a nap...")
            #     nap_time = 4*60
            #     while nap_time > 0:
            #         print('----', nap_time, 'nap seconds remaining ----')
            #         time.sleep(20)
            #         nap_time -= 20
