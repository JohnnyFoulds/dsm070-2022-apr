import sys
import time

import tornado

from miner import Miner
from node import Node
from connections import run_server, remote_connection

MINER_ADDRESS = # <--- put your address here

if __name__ == "__main__":
    if len(sys.argv) == 1:
        REMOTE_NODES = ["ws://ec2-18-135-206-224.eu-west-2.compute.amazonaws.com:46030/"]
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