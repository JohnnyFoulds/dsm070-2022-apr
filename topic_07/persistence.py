from typing import List

from pykka import ThreadingActor
from sqlitedict import SqliteDict

from blocks import Block
from transactions import Transaction


def dict_to_transaction(data: dict):
    return Transaction(
        bytes.fromhex(data["sender_hash"]),
        bytes.fromhex(data["recipient_hash"]),
        bytes.fromhex(data["sender_public_key"]),
        int(data["amount"]),
        int(data["fee"]),
        int(data["nonce"]),
        bytes.fromhex(data["signature"]),
        bytes.fromhex(data["txid"]))


def transaction_to_dict(transaction: Transaction) -> dict:
    return dict(
        sender_hash=transaction.sender_hash.hex(),
        recipient_hash=transaction.recipient_hash.hex(),
        sender_public_key=transaction.sender_public_key.hex(),
        amount=transaction.amount,
        fee=transaction.fee,
        nonce=transaction.nonce,
        signature=transaction.signature.hex(),
        txid=transaction.txid.hex())


def dict_to_block(data: dict) -> Block:
    return Block(
        bytes.fromhex(data["previous"]),
        int(data["height"]),
        bytes.fromhex(data["miner"]),
        list(map(dict_to_transaction, data["transactions"])),
        int(data["timestamp"]),
        int(data["difficulty"]),
        bytes.fromhex(data["block_id"]),
        int(data["nonce"]))


def block_to_dict(block: Block) -> dict:
    return dict(
        previous=block.previous.hex(),
        height=block.height,
        miner=block.miner.hex(),
        transactions=list(map(transaction_to_dict, block.transactions)),
        timestamp=block.timestamp,
        difficulty=block.difficulty,
        block_id=block.block_id.hex(),
        nonce=block.nonce)


class Persistence(ThreadingActor):
    def __init__(self, file_name):
        super().__init__()
        self.db = SqliteDict(file_name, autocommit=True)

    def get_blocks(self) -> List[Block]:
        height = 0
        blocks = []
        while True:
            block_dict = self.db.get(height)
            if block_dict is None:
                break
            blocks.append(dict_to_block(block_dict))
            height += 1
        return blocks

    def save_block(self, block: Block):
        self.db[block.height] = block_to_dict(block)

    def remove_block(self, height: int):
        del self.db[height]