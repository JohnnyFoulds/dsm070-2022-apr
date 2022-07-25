from typing import List, Optional, Dict

from pykka import ActorRef, ThreadingActor

from blockchain_state import BlockchainState, verify_reorg
from blocks import Block
from mempool import Mempool
from persistence import Persistence
from transactions import Transaction


class NodeStateSummary:
    def __init__(self, height: int, block_id: bytes, total_difficulty: int):
        self.height = height
        self.block_id = block_id
        self.total_difficulty = total_difficulty


class Node(ThreadingActor):
    def __init__(self, file_name):
        super().__init__()
        self.blockchain_state = BlockchainState([], dict(), 0)
        self.mempool = Mempool()
        self.connections: Dict[ActorRef, Optional[NodeStateSummary]] = dict()
        self.persistence = Persistence.start(file_name).proxy()
        for block in self.persistence.get_blocks().get():
            self.blockchain_state.verify_and_apply_block(block)

    def received_blocks(self, blocks: List[Block]):
        first_block = blocks[0]
        height = len(self.blockchain_state.longest_chain)
        assert first_block.height <= height, "No common block"

        while len(blocks) > 0 and blocks[0].height < height and blocks[0].block_id == self.blockchain_state.longest_chain[blocks[0].height].block_id:
            blocks = blocks[1:]

        if len(blocks) == 0:
            return

        if blocks[0].height == height:
            applied_blocks = []
            old_block_id = self.state_summary().block_id
            for block in blocks:
                try:
                    self.blockchain_state.verify_and_apply_block(block)
                except Exception as exception:
                    print("Block", block.block_id.hex(), "failed validation", exception)
                    break
                else:
                    applied_blocks.append(block)
                    self.persistence.save_block(block)

            if len(applied_blocks) != 0:
                for (connection, state) in self.connections.items():
                    if state is not None and state.block_id == old_block_id:
                        connection.proxy().send_blocks([block])

                new_state_summary = self.state_summary()

                for connection in self.connections:
                    connection.proxy().send_state_summary(new_state_summary)
        else:
            self.blockchain_state = verify_reorg(self.blockchain_state, blocks)

            for block in blocks:
                self.persistence.save_block(block)

            for to_remove in range(height, blocks[-1].height, -1):
                self.persistence.remove_block(to_remove)

            new_state_summary = self.state_summary()

            for connection in self.connections:
                connection.proxy().send_state_summary(new_state_summary)

        self.ask_for_better_chains()
        self.mempool.filter(self.blockchain_state.user_states)

    def state_summary(self) -> NodeStateSummary:
        height = len(self.blockchain_state.longest_chain)
        if height == 0:
            block_id = None
        else:
            block_id = self.blockchain_state.longest_chain[-1].block_id
        return NodeStateSummary(height, block_id, self.blockchain_state.total_difficulty)

    def get_blocks(self, start, end) -> List[Block]:
        return self.blockchain_state.longest_chain[start:end]

    def get_current_difficulty(self) -> int:
        return self.blockchain_state.calculate_difficulty()

    def received_node_state(self, connection: ActorRef, node_state_summary: NodeStateSummary):
        if connection not in self.connections:
            connection.proxy().send_state_summary(self.state_summary())

        self.connections[connection] = node_state_summary

        if node_state_summary.total_difficulty > self.blockchain_state.total_difficulty:
            connection.proxy().fetch_blocks(len(self.blockchain_state.longest_chain))

    def remove_connection(self, connection):
        if connection in self.connections.keys():
            self.connections.pop(connection)

    def current_difficulty(self):
        return self.blockchain_state.calculate_difficulty()

    def ask_for_better_chains(self):
        for connection, state in self.connections.items():
            if state is None:
                continue
            if state.total_difficulty > self.blockchain_state.total_difficulty:
                connection.proxy().fetch_blocks(len(self.blockchain_state.longest_chain))

    def get_transactions(self) -> List[Transaction]:
        return self.mempool.get_transactions()

    def received_transactions(self, transactions: List[Transaction]):
        accepted_transactions = []
        for transaction in transactions:
            try:
                sender_state = self.blockchain_state.user_states.get(transaction.sender_hash)
                transaction.verify(sender_state.balance, sender_state.nonce)
            except:
                print("Transaction", transaction.txid, "failed verification")
            else:
                if self.mempool.add_transaction(transaction):
                    accepted_transactions.append(transaction)

        if len(accepted_transactions) > 0:
            for connection in self.connections:
                connection.proxy().send_transactions(accepted_transactions)
