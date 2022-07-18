from datetime import time
from blocks import *
from transactions import *

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding

import unittest


def calculate_sha1_hash(public_key):
    digest = hashes.Hash(hashes.SHA1())
    digest.update(public_key)
    return digest.finalize()


def private_key_to_public_key(private_key):
    return private_key.public_key().public_bytes(encoding=Encoding.DER, format=PublicFormat.SubjectPublicKeyInfo)


def check_chain(difficulty, chain):
    state = dict()
    for block in chain:
        state.update(block.verify_and_get_changes(difficulty, state))
    return state


class BlocksTest(unittest.TestCase):
    def test_mine_block(self):
        alice = ec.generate_private_key(ec.SECP256K1)
        alice_address = calculate_sha1_hash(private_key_to_public_key(alice))

        block_1 = mine_block(bytes(32), 0, alice_address, [], int(time()), 100)
        states = block_1.verify_and_get_changes(100, dict())
        self.assertEqual(states[alice_address].balance, 10_000)

    def test_mine_block_with_transactions(self):
        alice = ec.generate_private_key(ec.SECP256K1)
        alice_address = calculate_sha1_hash(private_key_to_public_key(alice))
        bob = ec.generate_private_key(ec.SECP256K1)
        bob_address = calculate_sha1_hash(private_key_to_public_key(bob))

        transaction_1 = create_signed_transaction(alice, bob_address, 500, 10, 5)
        transaction_2 = create_signed_transaction(bob, alice_address, 300, 5, 0)
        block_1 = mine_block(bytes(32), 0, alice_address, [transaction_1, transaction_2], int(time()), 100)
        initial_states = dict([(alice_address, UserState(1000, 4))])
        states = block_1.verify_and_get_changes(100, initial_states)
        self.assertEqual(states[alice_address].balance, 1000 + 10_000 - 500 + 300 + 10)
        self.assertEqual(states[bob_address].balance, 500 - 10 - 300)

    def test_chain_1(self):
        chain = [
            Block(
                bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
                0,
                bytes.fromhex('dca5d2f1d7c2fea3c4e5d07211d33e03b04b5b2c'),
                [],
                1626625573,
                100000,
                bytes.fromhex('000001f6f7ca593dc0d280f9066b0109cc68b870c605bfc1a9c0636e7784b0ac'),
                76771),
            Block(
                bytes.fromhex('000001f6f7ca593dc0d280f9066b0109cc68b870c605bfc1a9c0636e7784b0ac'),
                1,
                bytes.fromhex('dca5d2f1d7c2fea3c4e5d07211d33e03b04b5b2c'),
                [
                    Transaction(
                        bytes.fromhex("dca5d2f1d7c2fea3c4e5d07211d33e03b04b5b2c"),
                        bytes.fromhex("bbd09baf141b979fc06552ad770f413be2747b6e"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a03420004e384194656d4aae5e849c0a897504ca3acf33075a734493f29bf25a4fe18961f71dad6eb1c4862bd353a81c1cc4ed1c4e6b6e868497d7992155bc74c5cf0a262"),
                        500,
                        10,
                        0,
                        bytes.fromhex(
                            "3046022100b2e6a016984065ba07c85116fe42f6e1220ce56d1c5f23913ce7e73bbd24a909022100dbd3879338e457d94fdb903951850d8ed6d763359d59fcbfd7287754be6cefba"),
                        bytes.fromhex("1ec611dee420082d895cb2178604d6a950036c32ab1fca7d74bcbf25d47a7e7d")),
                ],
                1626625574,
                100000,
                bytes.fromhex('000032fc68f00c792c69bd9d925f7d088a14d6526ee552e50cbdafaabf5e7461'),
                83198),
            Block(
                bytes.fromhex('000001f6f7ca593dc0d280f9066b0109cc68b870c605bfc1a9c0636e7784b0ac'),
                1,
                bytes.fromhex('bbd09baf141b979fc06552ad770f413be2747b6e'),
                [],
                1626625575,
                100000,
                bytes.fromhex('000053a44ff8a9bf30b47b3eb2f5915ac529e0ad6db5ec049b9d15183c17c46c'),
                4817)
        ]
        check_chain(100_000, chain)

    def test_chain_2(self):
        chain = [
            Block(
                bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
                0,
                bytes.fromhex('c8b8dae558379811b87078f8f1d42efe317708fc'),
                [],
                1626625905,
                100000,
                bytes.fromhex('0000506596cb0030ca58a487f7e96d094241113674262ed46954ae2394a5fe5a'),
                6163),
            Block(
                bytes.fromhex('0000506596cb0030ca58a487f7e96d094241113674262ed46954ae2394a5fe5a'),
                1,
                bytes.fromhex('c8b8dae558379811b87078f8f1d42efe317708fc'),
                [
                    Transaction(
                        bytes.fromhex("c8b8dae558379811b87078f8f1d42efe317708fc"),
                        bytes.fromhex("513b6466391c789085a54c8a91171c95e5165765"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a03420004ef0708a49ea290d99474334560c51763681e5bace0553c7cc529935afaddcc22ee64a08b113e0f6e74ce1099416cf4f117c2a682327e05aa22a4735f33a8bc9a"),
                        500,
                        10,
                        5,
                        bytes.fromhex(
                            "3046022100d9fbb398bc9f1c0d752f62cea01c77687b8a9812fe62261059ed8b2702383438022100b0f8bd031b644ac0b670b334e6994ee9ae2c3537de185b31fb57fb46c1df304a"),
                        bytes.fromhex("e6271384d5fafc912af80645495df57771d3053a7996172a4576ad66c6d3b674")),
                ],
                1626625905,
                100000,
                bytes.fromhex('00003ead300ff9d9a67fcd5bca85cea080ebba3326dee0969a1694e290ba438f'),
                34236)
        ]

        with self.assertRaisesRegex(Exception, "Invalid nonce"):
            check_chain(100_000, chain)

    def test_chain_3(self):
        chain = [
            Block(
                bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
                0,
                bytes.fromhex('4f3ea27a7af06cbe53911d4fb9326730d435255a'),
                [],
                1626626569,
                100000,
                bytes.fromhex('0000193f7397d8ed1a4991d91f8b8d2e55eb56915e884d435de7bbf0b183f335'),
                55419),
            Block(
                bytes.fromhex('0000193f7397d8ed1a4991d91f8b8d2e55eb56915e884d435de7bbf0b183f335'),
                1,
                bytes.fromhex('4f3ea27a7af06cbe53911d4fb9326730d435255a'),
                [
                    Transaction(
                        bytes.fromhex("4f3ea27a7af06cbe53911d4fb9326730d435255a"),
                        bytes.fromhex("9e09208d54c012c0844cf17cfbb175157516dc90"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a03420004f65e7817000dfb3d8a18ad79120f032f3f17fbefe86e176f4e2776a1fcdb55273b6820ee3661cfb1ccdbf847f2c2271a52d4b981dc27640afd67fcbcafb80c68"),
                        500,
                        10,
                        0,
                        bytes.fromhex(
                            "3045022100a28415cb2e887e1e26a3b2c115cf01d6d7a88ebff82f5d207a0ad5dc43991a160220382d8d92124ba0e166822f463fee492f51c587fbddede088181c7136898a943c"),
                        bytes.fromhex("adc3a16f4e41eee845855bb216af3a6486f2412ae99b09574affdde0b777bce7")),
                    Transaction(
                        bytes.fromhex("9e09208d54c012c0844cf17cfbb175157516dc90"),
                        bytes.fromhex("4f3ea27a7af06cbe53911d4fb9326730d435255a"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a034200041a719dc420fdbdeef447e90a6368b9486d4afbacd900f6d9d5f62692dfa9ecb695999af4fcf61bdc523021b3aef2b84344b7c4ba7d3a36efe2e5f3eff50e8c54"),
                        100,
                        10,
                        0,
                        bytes.fromhex(
                            "3045022100d7106f0f7a62bc14f693539207f5cc7c9b9507cc3c1eeb635ebb3e4a2a9f2506022028bad456d1badf020baf39d67b169325f55aff8cc52d2c192a2aa036ad1932c9"),
                        bytes.fromhex("bf972224d8b6ce9632bf94d96d86f382452c8b47733696bec19dd4e1da9b147d")),
                ],
                1626626570,
                100000,
                bytes.fromhex('00003449e333998777dc2d627a2642979ce435373ffee834b6943a12875901b5'),
                145399),
            Block(
                bytes.fromhex('0000193f7397d8ed1a4991d91f8b8d2e55eb56915e884d435de7bbf0b183f335'),
                1,
                bytes.fromhex('4f3ea27a7af06cbe53911d4fb9326730d435255a'),
                [
                    Transaction(
                        bytes.fromhex("9e09208d54c012c0844cf17cfbb175157516dc90"),
                        bytes.fromhex("4f3ea27a7af06cbe53911d4fb9326730d435255a"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a034200041a719dc420fdbdeef447e90a6368b9486d4afbacd900f6d9d5f62692dfa9ecb695999af4fcf61bdc523021b3aef2b84344b7c4ba7d3a36efe2e5f3eff50e8c54"),
                        390,
                        5,
                        1,
                        bytes.fromhex(
                            "3045022100fae9ab97090f2f0fb5715497e12a06438cbccc610bae2f9c019dfa5bdb40f0090220283f5498f22e17ac9ecf4c239d864811dd47cb0ccb8c3584794791fd171e6b90"),
                        bytes.fromhex("0cfd04ed0b2b279c12412687c770b1224c8bfed453292652694339ddade4d63a")),
                ],
                1626626571,
                100000,
                bytes.fromhex('000071f1c701e06e5b91adb4289d6c5227b614bd4441748923826e5d0e8828da'),
                83651),
        ]
        check_chain(100_000, chain)

    def test_chain_4(self):
        chain = [
            Block(
                bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
                0,
                bytes.fromhex('433a72a399823750c766bfa9f27b3948055fbb4b'),
                [],
                1626626687,
                100000,
                bytes.fromhex('00004da06fbf33417944e094cd6ea021aa72e6ef33fcf5bfac277bcd6067429f'),
                62969),
            Block(
                bytes.fromhex('00004da06fbf33417944e094cd6ea021aa72e6ef33fcf5bfac277bcd6067429f'),
                1,
                bytes.fromhex('433a72a399823750c766bfa9f27b3948055fbb4b'),
                [
                    Transaction(
                        bytes.fromhex("433a72a399823750c766bfa9f27b3948055fbb4b"),
                        bytes.fromhex("62b2c702c43e07df61231065fedbff2fa3d6ddcd"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a03420004657a0dc0dbd52f9bcd87e375c65b50057e5caad07cc552f3a359b0b48f9c2b22c5cea0031221313cb9ed8d749f7f57698cf50d486772f23bee5f40ff6865f4e1"),
                        500,
                        10,
                        0,
                        bytes.fromhex(
                            "3045022052e37971f30b823d6633d1872c0cc90a90505c2969ffb36a505d979798f29d0d022100d3df832c1dcef7cf98764012c6f55d8028c84bbc94c0b486e6c531b4abfe4227"),
                        bytes.fromhex("bb0b351dc7acc25d0bdc6f18845bd7d9ff66b2c0be912dda14f64e09556409e6")),
                    Transaction(
                        bytes.fromhex("62b2c702c43e07df61231065fedbff2fa3d6ddcd"),
                        bytes.fromhex("433a72a399823750c766bfa9f27b3948055fbb4b"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a03420004705ca6c323d3ebe9b8159c4bdfde5cd06b853d9d3791b9d7c6e890ea8db94c063e3ebf18f342896e652819b94c7ebaa14739fc395b9c62c99c0e665234cd1926"),
                        100,
                        10,
                        0,
                        bytes.fromhex(
                            "3044022061461644fe80c89c3669881d37dd7e5ac61062ecf04e581adf340e8cc61157a80220507b4b16e98c8c87615bc21d7b06f48a21ca772b229fe28230d39cd7e0b97c30"),
                        bytes.fromhex("46dc641178a95aeccb86e1381d5fa156767ef716e42beffd1d15166af21fa601")),
                ],
                1626626687,
                100000,
                bytes.fromhex('00008caae70cc7535f79b5f69d20bb504ff3840b5404a4bcfc1b2a6715ada148'),
                163463),
            Block(
                bytes.fromhex('00004da06fbf33417944e094cd6ea021aa72e6ef33fcf5bfac277bcd6067429f'),
                1,
                bytes.fromhex('433a72a399823750c766bfa9f27b3948055fbb4b'),
                [
                    Transaction(
                        bytes.fromhex("62b2c702c43e07df61231065fedbff2fa3d6ddcd"),
                        bytes.fromhex("433a72a399823750c766bfa9f27b3948055fbb4b"),
                        bytes.fromhex(
                            "3056301006072a8648ce3d020106052b8104000a03420004705ca6c323d3ebe9b8159c4bdfde5cd06b853d9d3791b9d7c6e890ea8db94c063e3ebf18f342896e652819b94c7ebaa14739fc395b9c62c99c0e665234cd1926"),
                        391,
                        5,
                        1,
                        bytes.fromhex(
                            "3046022100c2ebb8f98ae24248e870cabec81997654a072d8bfe3bdd89691c78ba6ba7b815022100ab044396b5a8e409db20c8d139b2a7e391baff9297c3ec770ec2c83ab7a12ec3"),
                        bytes.fromhex("acd668df31c92502725af299466d161b3c2485e9ad3eb5be6dbc1012263226f5")),
                ],
                1626626689,
                100000,
                bytes.fromhex('00001a7e5d78c0ef8215cfbb50f7d1795cf0d6b21d8f89d9617dd74ce00649b3'),
                141597),
        ]
        with self.assertRaisesRegex(Exception, "Balance too small"):
            check_chain(100_000, chain)

    def test_chain_5(self):
        chain = [
            Block(
                bytes.fromhex('0000000000000000000000000000000000000000000000000000000000000000'),
                0,
                bytes.fromhex('3ea5cf80f3c66d7cc1781c73cf288422f19a862b'),
                [],
                1626626863,
                100000,
                bytes.fromhex('002a1823e815f9bed9458637f4d44a5aa249a74363bc0692a822898d0bca47f1'),
                185),
        ]

        with self.assertRaisesRegex(Exception, "Invalid proof of work"):
            check_chain(100_000, chain)


if __name__ == '__main__':
    unittest.main(exit=False)
