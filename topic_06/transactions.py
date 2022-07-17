"""
This module define the Transaction class.
"""

from __future__ import annotations
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.exceptions import InvalidSignature


class Transaction:
    """
    Zimcoin transaction class.
    """
    def __init__(self, sender_hash:bytes, recipient_hash:bytes,
                 sender_public_key:bytes, amount:int, fee:int, nonce:int,
                 signature, txid):
        self.sender_hash = sender_hash
        self.recipient_hash = recipient_hash
        self.sender_public_key = sender_public_key
        self.amount = amount
        self.fee = fee
        self.nonce = nonce
        self.signature = signature
        self.txid = txid

    def verify(self, sender_balance:int, sender_previous_nonce:int) -> bool:
        """
        Verify that the transaction is valid.
        """
        # sender and recipient validation
        if len(self.sender_hash) != 20:
            raise ValueError('Invalid sender hash')
        if len(self.recipient_hash) != 20:
            raise ValueError('Invalid recipient hash')

        # validate the sender hash
        if self.sender_hash != hashlib.sha1(self.sender_public_key).digest():
            raise ValueError('The sender hash is not computed correctly')

        # amount validation
        if self.amount < 1:
            raise ValueError('Invalid amount')
        if self.amount > sender_balance:
            raise ValueError('Insufficient funds')
        if not float(self.amount).is_integer():
            raise ValueError('The amount should be a whole number')

        # fee validation
        if self.fee < 0:
            raise ValueError('Invalid fee')
        if self.fee > self.amount:
            raise ValueError('The fee should be less than the amount')
        if not float(self.fee).is_integer():
            raise ValueError('The fee should be a whole number')

        # nonce validation
        if self.nonce <= sender_previous_nonce:
            raise ValueError('Invalid nonce')
        if self.nonce > sender_previous_nonce + 1:
            raise ValueError('Invalid nonce')

        # verify the transaction id
        if self.txid != self.create_txid():
            raise ValueError('The transaction ID is invalid')

        # validate the signature
        try:
            sender_public_key = load_der_public_key(self.sender_public_key)
            sender_public_key.verify(
                self.signature,
                self.create_signature_hash(),
                ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        except InvalidSignature as invalid_signature:
            raise ValueError('The signature is invalid') from invalid_signature

        return True

    def create_txid(self) -> bytes:
        """
        Create a hash of the transaction.
        """
        # create a hash of the transaction
        txid = hashes.Hash(hashes.SHA256())
        txid.update(self.sender_hash)
        txid.update(self.recipient_hash)
        txid.update(self.sender_public_key)
        txid.update(self.amount.to_bytes(8, byteorder='little', signed=False))
        txid.update(self.fee.to_bytes(8, byteorder='little', signed=False))
        txid.update(self.nonce.to_bytes(8, byteorder='little', signed=False))
        txid.update(self.signature)

        return txid.finalize()

    def create_signature_hash(self) -> bytes:
        """
        Create a hash of the recipient transaction data.
        """
        recipient_hash = hashes.Hash(hashes.SHA256())
        recipient_hash.update(self.recipient_hash)
        recipient_hash.update(self.amount.to_bytes(8, byteorder='little', signed=False))
        recipient_hash.update(self.fee.to_bytes(8, byteorder='little', signed=False))
        recipient_hash.update(self.nonce.to_bytes(8, byteorder='little', signed=False))

        return recipient_hash.finalize()

    @staticmethod
    def create_signed_transaction(sender_private_key:ec.EllipticCurvePrivateKey,
                                  recipient_hash:bytes, amount:int, fee:int,
                                  nonce:int) -> Transaction:
        """
        Create a signed transaction.
        """
        # validate the amount
        if amount < 0:
            raise ValueError('Invalid amount')
        if not float(amount).is_integer():
            raise ValueError('The amount should be a whole number')

        # fee validation
        if fee < 0:
            raise ValueError('Invalid fee')
        if not float(fee).is_integer():
            raise ValueError('The fee should be a whole number')

        # get the public key
        public_key = sender_private_key.public_key()
        sender_public_key = public_key.public_bytes(
                encoding=Encoding.DER,
                format=PublicFormat.SubjectPublicKeyInfo)

        # create the new transaction
        transaction = Transaction(
            sender_hash = hashlib.sha1(sender_public_key).digest(),
            recipient_hash = recipient_hash,
            sender_public_key = sender_public_key,
            amount = amount,
            fee = fee,
            nonce = nonce,
            signature = None,
            txid = None)

        # sign the transaction
        transaction.signature = sender_private_key.sign(
            transaction.create_signature_hash(),
            ec.ECDSA(utils.Prehashed(hashes.SHA256()))
        )

        # create the transaction id
        transaction.txid = transaction.create_txid()

        return transaction
