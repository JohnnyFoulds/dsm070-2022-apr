from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding


class Transaction:
    def __init__(self, sender_hash: bytes, recipient_hash: bytes, sender_public_key: bytes,
                 amount: int, fee: int, nonce: int, signature: bytes, txid: bytes):
        self.sender_hash = sender_hash
        self.recipient_hash = recipient_hash
        self.sender_public_key = sender_public_key
        self.amount = amount
        self.fee = fee
        self.nonce = nonce
        self.signature = signature
        self.txid = txid

    def verify(self, sender_balance, sender_previous_nonce):
        assert self.amount <= sender_balance, \
            f"Sender's balance of {sender_balance} does not cover amount ({self.amount})"
        assert self.fee <= self.amount, \
            f"Fee {self.fee} exceeds amount ({self.amount})"
        assert self.nonce == sender_previous_nonce + 1, \
            f"Sender's nonce of {sender_previous_nonce} does not match expected ({self.nonce})"


def calculate_sha1_hash(public_key: bytes):
    digest = hashes.Hash(hashes.SHA1())
    digest.update(public_key)
    return digest.finalize()


def create_signed_transaction(sender_private_key, recipient_hash, amount, fee, nonce):
    sender_public_key = sender_private_key.public_key().public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)
    sender_hash = calculate_sha1_hash(sender_public_key)

    return Transaction(sender_hash, recipient_hash, b'abcd' * 8, amount, fee, nonce, b'abcd' * 20, b'abcd'*8)
