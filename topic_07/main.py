import sys
import time

import tornado

from miner import Miner
from node import Node
from connections import run_server, remote_connection

MINER_ADDRESS = b's\\s\x884u\x19\x11m\xad\xedA\x8c\x8f\xe5\x84k^]m'
#MINER_ADDRESS = bytes.fromhex('dca5d2f1d7c2fea3c4e5d07211d33e03b04b5b2c')
#MINER_ADDRESS = bytes.fromhex('501ace0000000000000000000000000000000000')

if __name__ == "__main__":
    if len(sys.argv) == 1:
        REMOTE_NODES = ["ws://node.zimcoin.org:46030/"]
        node = Node.start("./blocks.sqlite").proxy()
        miner = Miner.start(node, MINER_ADDRESS).proxy()

        for remote in REMOTE_NODES:
            remote_connection(node, remote)
        miner.start_mining()

        tornado.ioloop.IOLoop.current().start()
    elif sys.argv[1] == 'server':
        PORT = 46030
        REMOTE_NODES = []
        node = Node.start("./blocks.sqlite").proxy()
        miner = Miner.start(node, MINER_ADDRESS).proxy()
        miner.start_mining()
        run_server(node, PORT)
    else:
        print("Unknown command")
