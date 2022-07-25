from typing import Optional, List, Dict

from blocks import UserState
from transactions import Transaction

MAX_TRANSACTIONS = 50


class Mempool:
    def __init__(self):
        self.by_sender: dict[bytes, Transaction] = dict()

    def get_min_fee(self) -> Optional[Transaction]:
        min_fee_transaction = None
        for transaction in self.by_sender.values():
            if min_fee_transaction is None or min_fee_transaction.fee > transaction.fee:
                min_fee_transaction = transaction
        return min_fee_transaction

    def add_transaction(self, transaction: Transaction) -> bool:
        if transaction.sender_hash in self.by_sender:
            old_transaction = self.by_sender[transaction.sender_hash]
            if old_transaction.fee < transaction.fee:
                self.by_sender[transaction.sender_hash] = transaction
                return True
            return False
        else:
            if len(self.by_sender) < MAX_TRANSACTIONS:
                self.by_sender[transaction.sender_hash] = transaction
                return True

            min_fee_transaction = self.get_min_fee()
            if min_fee_transaction.fee < transaction.fee:
                self.by_sender[transaction.sender_hash] = transaction
                del self.by_sender[min_fee_transaction.sender_hash]
                return True
            return False

    def filter(self, user_states: Dict[bytes, UserState]):
        new_transactions = dict()
        for transaction in self.by_sender.values():
            try:
                state = user_states[transaction.sender_hash]
                transaction.verify(state.balance, state.nonce)
            except:
                print("Removing transaction", transaction.txid, "from mempool")
            else:
                new_transactions[transaction.sender_hash] = transaction
        self.by_sender = new_transactions

    def get_transactions(self) -> List[Transaction]:
        return list(self.by_sender.values())