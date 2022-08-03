import json
from typing import List

import tornado
from pykka import ThreadingActor
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.websocket import WebSocketHandler, websocket_connect, WebSocketClientConnection

from blocks import Block
from node import NodeStateSummary
from persistence import block_to_dict, dict_to_block, transaction_to_dict, dict_to_transaction
from transactions import Transaction

MAX_BLOCKS = 50
MAX_BLOCK_IDS = 100


class ConnectionActor(ThreadingActor):
    def __init__(self, connection_handler, node):
        super().__init__()
        self.node_server = connection_handler
        self.ioloop = IOLoop.current()
        self.node = node

    def send_state_summary(self, summary: NodeStateSummary):
        if summary.block_id is None:
            block_id = None
        else:
            block_id = summary.block_id.hex()
        self.send(json.dumps(dict(
            type='update_state',
            height=summary.height,
            block_id=block_id,
            total_difficulty=summary.total_difficulty
        )))

    def send_block_ids(self, start: int, block_ids: List[bytes]):
        self.send(json.dumps(dict(
            type='block_ids',
            start=start,
            block_ids=list(map(lambda x: x.hex(), block_ids))
        )))

    def send_blocks(self, blocks: List[Block]):
        self.send(json.dumps(dict(
            type='blocks',
            blocks=list(map(block_to_dict, blocks))
        )))

    def fetch_blocks(self, height):
        self.send(json.dumps(dict(
            type='get_blocks',
            start=height - MAX_BLOCKS // 2,
            end=height + MAX_BLOCKS // 2,
        )))

    def send_transactions(self, transactions: List[Transaction]):
        self.send(json.dumps(dict(
            type='transactions',
            transactions=list(map(transaction_to_dict, transactions))
        )))

    def fetch_transactions(self):
        self.send(json.dumps(dict(
            type='get_transactions'
        )))

    def send(self, message):
        print("Sending", message)
        self.ioloop.add_callback(self.node_server.write_message, message)

    def on_stop(self) -> None:
        self.node.remove_connection(self.actor_ref)

    def handle_message(self, message):
        parsed = json.loads(message)
        print("Got message", parsed)

        if parsed["type"] == 'update_state':
            if parsed["block_id"] == None:
                block_id = None
            else:
                block_id = bytes.fromhex(parsed["block_id"])
            summary = NodeStateSummary(
                int(parsed["height"]),
                block_id,
                int(parsed["total_difficulty"]))
            self.node.received_node_state(self.actor_ref, summary)
        elif parsed["type"] == 'get_block_ids':
            start = int(parsed["start"])
            assert start >= 0
            end = min(int(parsed["end"]), start + MAX_BLOCK_IDS)
            assert end >= 0

            blocks = self.node.get_blocks(start, end).get()
            self.send_block_ids(start, list(map(lambda block: block.block_id, blocks)))
        elif parsed["type"] == 'get_blocks':
            start = max(0, int(parsed["start"]))
            end = min(int(parsed["end"]), start + MAX_BLOCKS)
            assert end >= 0

            blocks = self.node.get_blocks(start, end).get()
            self.send_blocks(blocks)
        elif parsed["type"] == 'blocks':
            blocks = list(map(dict_to_block, parsed["blocks"]))
            self.node.received_blocks(blocks)
        elif parsed["type"] == 'get_transactions':
            transactions = self.node.get_transactions().get()
            self.node.send_transactions(transactions)
        elif parsed["type"] == 'transactions':
            transactions = list(map(dict_to_transaction, parsed["transactions"]))
            self.node.received_transactions(transactions)


class ConnectionHandler(WebSocketHandler):
    def initialize(self, node):
        print("Initialize")
        self.node = node

    def open(self):
        connection_actor = ConnectionActor.start(self, self.node)
        self.connection = connection_actor.proxy()
        print("Opened connection", id(self))

    def on_message(self, message: str):
        self.connection.handle_message(message)

    def on_close(self):
        print("Connection closed", id(self))
        self.connection.stop()

    def check_origin(self, origin: str) -> bool:
        return True

def run_server(node, port):
    app = Application([
        (r'/', ConnectionHandler, dict(node=node)),
    ])
    app.listen(port, "0.0.0.0")
    tornado.ioloop.IOLoop.current().start()


def remote_connection(node, address):
    connection = None

    def connect_callback(connection_handler):
        nonlocal connection
        connection_handler: WebSocketClientConnection = connection_handler.result()
        connection = ConnectionActor.start(connection_handler, node).proxy()
        connection.send_state_summary(node.state_summary().get())
        connection.fetch_transactions()

    def on_message_callback(message: str):
        connection.handle_message(message)

    websocket_connect(address, callback=connect_callback, on_message_callback=on_message_callback)
