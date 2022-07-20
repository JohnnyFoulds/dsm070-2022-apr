"""
Test cases take from the previous assignment to verify the transaction
class.
"""

from __future__ import annotations
import unittest
import copy
import hashlib
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric import ec
from transactions import Transaction

class InitialTransactionTests(unittest.TestCase):
    """
    The first set of tests created while writing the code.
    """

    def setUp(self):
        # create a new private key for testing
        self.private_key = ec.generate_private_key(ec.SECP256K1)
        self.recipient_hash = bytes.fromhex("3df8f04b3c159fdc6631c4b8b0874940344d173d")

        # create the sample transaction
        self.tx = Transaction(
            sender_hash=bytes.fromhex("3df8f04b3c159fdc6631c4b8b0874940344d173d"),
            recipient_hash=bytes.fromhex("5c1499a0484ace2f731b0afb83241e15f0e168ca"),
            sender_public_key=bytes.fromhex("3056301006072a8648ce3d020106052b8104000a" +
                                            "03420004886ed03cb7ffd4cbd95579ea2e202f1d" +
                                            "b29afc3bf5d7c2c34a34701bbb0685a7b535f1e6" +
                                            "31373afe8d1c860a9ac47d8e2659b74d437435b0" +
                                            "5f2c55bf3f033ac1"),
            amount=10,
            fee=2,
            nonce=5,
            signature=bytes.fromhex("3046022100f9c076a72a2341a1b8cb68520713e1" +
                                    "2f173378cf78cf79c7978a2337fbad141d022100" +
                                    "ec27704d4d604f839f99e62c02e65bf60cc93ae1"
                                    "735c1ccf29fd31bd3c5a40ed"),
            txid=bytes.fromhex("ca388e0890b71bd1775460d478f26af3776c9b4f" +
                               "6c2b936e1e788c5c87657bc3"))

    def create_test_transaction(self, amount:int, fee:int, nonce:int):
        """
        Create a test transaction.
        """
        return Transaction.create_signed_transaction(
            sender_private_key=self.private_key,
            recipient_hash=self.recipient_hash,
            amount=amount,
            fee=fee,
            nonce=nonce)

    def test_create_signed_transaction(self):
        """
        Test the creation of a new signed transaction.
        """
        # create a new transaction
        tx = Transaction.create_signed_transaction(
            sender_private_key=self.private_key,
            recipient_hash=self.recipient_hash,
            amount=33,
            fee=6,
            nonce=15)

        # validate the transaction
        tx.verify(300, 14)

    def test_verify_sender_hash(self):
        """
        Test that the sender_hash is verified correctly.
        """
        # test a valid hash
        self.tx.sender_hash = bytes.fromhex("3df8f04b3c159fdc6631c4b8b0874940344d173d")
        self.tx.verify(
            sender_balance=100,
            sender_previous_nonce=4)

        # test a sender_hash that do not match the public key
        self.tx.sender_hash = bytes.fromhex("5c1499a0484ace2f731b0afb83241e15f0e168ca")
        with self.assertRaisesRegex(ValueError, 'The sender hash is not computed correctly'):
            self.tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

        # test an invalid hash
        self.tx.sender_hash = bytearray(b'thequickbrownfox')
        with self.assertRaisesRegex(ValueError, 'Invalid sender hash'):
            self.tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

    def test_verify_recipient_hash(self):
        """
        Test that the recipient_hash is verified correctly.
        """
        # test a valid hash
        self.tx.recipient_hash = bytes.fromhex("5c1499a0484ace2f731b0afb83241e15f0e168ca")
        self.tx.verify(
            sender_balance=100,
            sender_previous_nonce=4)

        # test an invalid hash
        self.tx.recipient_hash = bytearray(b'thequickbrownfox')
        with self.assertRaisesRegex(ValueError, 'Invalid recipient hash'):
            self.tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

    def test_verify_amount(self):
        """
        Test that the amount is verified correctly.
        """
        # test a valid amount
        with self.subTest('Test for a valid amount'):
            tx = self.create_test_transaction(amount=50, fee=2, nonce=5)
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

        with self.subTest('The amount should be a whole number'):
            with self.assertRaisesRegex(ValueError, 'The amount should be a whole number'):
                tx = self.create_test_transaction(amount=50.1, fee=2, nonce=5)
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.subTest('The amount should be between 1 and sender_balance'):
            with self.assertRaisesRegex(ValueError, 'Invalid amount'):
                tx = self.create_test_transaction(amount=0, fee=2, nonce=5)
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

            with self.assertRaisesRegex(ValueError, 'Invalid amount'):
                tx = self.create_test_transaction(amount=-10, fee=2, nonce=5)
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

            with self.assertRaisesRegex(ValueError, 'Balance too small'):
                tx = self.create_test_transaction(amount=101, fee=2, nonce=5)
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

    def test_verify_fee(self):
        """
        Test that the fee is verified correctly.
        """
        with self.subTest('Test for a valid fee'):
            tx = self.create_test_transaction(amount=50, fee=5, nonce=5)
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

        with self.subTest('The fee can be zero'):
            tx = self.create_test_transaction(amount=50, fee=0, nonce=5)
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

        with self.subTest('The fee should be a whole number'):
            with self.assertRaisesRegex(ValueError, 'The fee should be a whole number'):
                tx = self.create_test_transaction(amount=50, fee=10.1, nonce=5)
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.subTest('The fee should be between 0 and amount'):
            with self.assertRaisesRegex(ValueError, 'Invalid fee'):
                tx = self.create_test_transaction(amount=50, fee=-10, nonce=5)
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.assertRaisesRegex(ValueError, 'The fee should be less than the amount'):
            tx = self.create_test_transaction(amount=50, fee=51, nonce=5)
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

    def test_verify_nonce(self):
        """
        Verify that the nonce is a valid value.
        """
        tx = self.create_test_transaction(amount=50, fee=5, nonce=10)

        # test a valid nonce
        with self.subTest('Test for a valid fee'):
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=9)

        with self.subTest('The nonce should be sender_previous_nonce + 1'):
            with self.assertRaisesRegex(ValueError, 'Invalid nonce'):
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=8)

            with self.assertRaisesRegex(ValueError, 'Invalid nonce'):
                tx.verify(
                    sender_balance=100,
                    sender_previous_nonce=11)

    def test_create_txid(self):
        """
        Test Create a transaction id.
        """
        self.assertEqual(self.tx.create_txid(), self.tx.txid)

        # the transaction should not match if one of the values differ
        self.tx.fee = 3
        self.assertNotEqual(self.tx.create_txid(), self.tx.txid)

    def test_verify_txid(self):
        """
        Test that the txid is computed correctly.
        """
        # create a valid transaction
        with self.subTest('Test for a valid transaction'):
            tx = self.create_test_transaction(amount=50, fee=2, nonce=5)
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=4)

        with self.subTest('Test with a different sender hash'):
            with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
                tx_invalid = copy.deepcopy(tx)
                tx_invalid.sender_hash = self.tx.sender_hash
                tx_invalid.sender_public_key = self.tx.sender_public_key

                tx_invalid.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.subTest('Test with a different recipient hash'):
            with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
                tx_invalid = copy.deepcopy(tx)
                tx_invalid.recipient_hash = self.tx.recipient_hash

                tx_invalid.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.subTest('Test with a different amount'):
            with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
                tx_invalid = copy.deepcopy(tx)
                tx_invalid.amount = tx_invalid.amount + 1

                tx_invalid.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.subTest('Test with a different fee'):
            with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
                tx_invalid = copy.deepcopy(tx)
                tx_invalid.fee = tx_invalid.fee + 1

                tx_invalid.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

        with self.subTest('Test with a different signature'):
            with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
                tx_invalid = copy.deepcopy(tx)
                tx_invalid.signature = self.tx.signature

                tx_invalid.verify(
                    sender_balance=100,
                    sender_previous_nonce=4)

class CourseworkTransactionTests(unittest.TestCase):
    """
    Perform the tests as required by assignment 2.
    """

    def create_valid_transaction(self,
            sender_private_key:ec.EllipticCurvePrivateKey=None, amount:int=10,
            fee:int=1, nonce:int=2) -> Transaction:
        """
        Create a valid transaction.
        """
        # create a private keys
        if sender_private_key is None:
            sender_private_key = ec.generate_private_key(ec.SECP256K1())

        recipient_private_key = ec.generate_private_key(ec.SECP256K1())

        # get the recipient hash
        recipient_hash = hashlib.sha1(
            recipient_private_key.public_key().public_bytes(
                encoding=Encoding.DER,
                format=PublicFormat.SubjectPublicKeyInfo)).digest()

        # create the transaction
        return Transaction.create_signed_transaction(
            sender_private_key=sender_private_key,
            recipient_hash=recipient_hash,
            amount=amount,
            fee=fee,
            nonce=nonce)

    def test_create_signed_transaction(self):
        """
        Generate a private key using ec.generate_private_key(ec.SECP256K1) . Call
        create_signed_transaction to make a test transaction. Check that the
        transaction.verify call succeeds (when provided with a sender_balance which is
        sufficiently high and sender_previous_nonce = transaction.nonce - 1 ).
        """
        # create a sender private
        sender_private_key = ec.generate_private_key(ec.SECP256K1())

        # create a transaction
        tx = self.create_valid_transaction(sender_private_key=sender_private_key)

        # verify the transaction
        self.assertTrue(
            tx.verify(
                sender_balance=100,
                sender_previous_nonce=tx.nonce - 1))

    def test_verify_txid(self):
        """
        Generate a valid transaction, check that modifying any of the fields causes
        transaction.verify to raise an exception due to an invalid txid.
        """
        # create a valid transaction
        tx = self.create_valid_transaction()
        tx.verify(sender_balance=100, sender_previous_nonce=tx.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The sender hash is not computed correctly'):
            tx_invalid = copy.deepcopy(tx)
            tx_invalid.sender_hash = bytes.fromhex("3df8f04b3c159fdc6631c4b8b0874940344d173d")
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
            tx_invalid.sender_public_key=bytes.fromhex("3056301006072a8648ce3d020106052b8104000a" +
                                            "03420004886ed03cb7ffd4cbd95579ea2e202f1d" +
                                            "b29afc3bf5d7c2c34a34701bbb0685a7b535f1e6" +
                                            "31373afe8d1c860a9ac47d8e2659b74d437435b0" +
                                            "5f2c55bf3f033ac1")
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
            tx_invalid = copy.deepcopy(tx)
            tx_invalid.recipient_hash = bytes.fromhex("5c1499a0484ace2f731b0afb83241e15f0e168ca")
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
            tx_invalid = copy.deepcopy(tx)
            tx_invalid.amount = tx_invalid.amount + 1
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
            tx_invalid = copy.deepcopy(tx)
            tx_invalid.fee = tx_invalid.fee + 1
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
            tx_invalid = copy.deepcopy(tx)
            tx_invalid.nonce = tx_invalid.nonce + 1
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

        with self.assertRaisesRegex(ValueError, 'The transaction ID is invalid'):
            tx_invalid = copy.deepcopy(tx)
            tx_invalid.signature = bytes.fromhex("3046022100f9c076a72a2341a1b8cb68520713e1" +
                                    "2f173378cf78cf79c7978a2337fbad141d022100" +
                                    "ec27704d4d604f839f99e62c02e65bf60cc93ae1"
                                    "735c1ccf29fd31bd3c5a40ed")
            tx_invalid.verify(sender_balance=100, sender_previous_nonce=tx_invalid.nonce-1)

    def test_invalid_signature(self):
        """"
        Generate a valid transaction, change the amount field, regenerate the txid so it is valid
        again. Check that transaction.verify raises an exception due to an invalid signature.
        """
        # create a valid transaction
        tx = self.create_valid_transaction(amount=50)
        tx.verify(sender_balance=100, sender_previous_nonce=tx.nonce-1)

        # change the amount and regenerate the txid
        tx.amount = 5
        tx.txid = tx.create_txid()

        with self.assertRaisesRegex(ValueError, 'The signature is invalid'):
            tx.verify(sender_balance=100, sender_previous_nonce=tx.nonce-1)

    def test_invalid_sender_balance(self):
        """
        Generate a valid transaction, check that transaction.verify raises an exception if either
        the sender_balance is too low or sender_previous_nonce is incorrect.
        """
        # create a valid transaction
        tx = self.create_valid_transaction(amount=50)
        tx.verify(sender_balance=100, sender_previous_nonce=tx.nonce-1)

        # verify with a balance that is too low
        with self.assertRaisesRegex(ValueError, 'Balance too small'):
            tx.verify(sender_balance=10, sender_previous_nonce=tx.nonce-1)

        # verify with a previous nonce that is incorrect
        with self.assertRaisesRegex(ValueError, 'Invalid nonce'):
            tx.verify(sender_balance=100, sender_previous_nonce=55)

    def test_invalid_new_signature(self):
        """
        Generate two private keys, A and B . Use A to generate a valid transaction. Replace the
        signature with a signature created using B . Regenerate the txid and confirm that
        transaction.verify fails with an invalid signature.
        """
        # create private keys
        private_key_a = ec.generate_private_key(ec.SECP256K1())
        private_key_b = ec.generate_private_key(ec.SECP256K1())

        # create transactions
        tx_a = self.create_valid_transaction(sender_private_key=private_key_a)
        tx_b = self.create_valid_transaction(sender_private_key=private_key_b)

        # both transactions should be valid
        tx_a.verify(sender_balance=100, sender_previous_nonce=tx_a.nonce-1)
        tx_b.verify(sender_balance=100, sender_previous_nonce=tx_b.nonce-1)

        # change the signature of tx_a to match tx_b and update the txid
        tx_a.signature = tx_b.signature
        tx_a.txid = tx_a.create_txid()

        # verify that tx_a is invalid
        with self.assertRaisesRegex(ValueError, 'The signature is invalid'):
            tx_a.verify(sender_balance=100, sender_previous_nonce=tx_a.nonce-1)

    def test_model_transaction(self):
        """
        Check that the following transaction verifies successfully (when using sender_balance = 20 ,
        sender_previous_nonce = 4 )
        """
        # create the model transaction
        tx = Transaction(
            bytes.fromhex("3df8f04b3c159fdc6631c4b8b0874940344d173d"),
            bytes.fromhex("5c1499a0484ace2f731b0afb83241e15f0e168ca"),
            bytes.fromhex("3056301006072a8648ce3d020106052b8104000a" +
                          "03420004886ed03cb7ffd4cbd95579ea2e202f1d" +
                          "b29afc3bf5d7c2c34a34701bbb0685a7b535f1e6" +
                          "31373afe8d1c860a9ac47d8e2659b74d437435b0" +
                          "5f2c55bf3f033ac1"),
            10,
            2,
            5,
            bytes.fromhex("3046022100f9c076a72a2341a1b8cb68520713e1" +
                           "2f173378cf78cf79c7978a2337fbad141d022100" +
                           "ec27704d4d604f839f99e62c02e65bf60cc93ae1"
                           "735c1ccf29fd31bd3c5a40ed"),
            bytes.fromhex("ca388e0890b71bd1775460d478f26af3776c9b4f" +
                          "6c2b936e1e788c5c87657bc3"))

        # verify the transaction
        self.assertTrue(tx.verify(sender_balance=20, sender_previous_nonce=4))
