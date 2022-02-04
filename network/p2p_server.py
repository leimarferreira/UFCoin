import asyncio
import json
from typing import Any, List

import websockets
from model import Block
from model.transaction import Transaction
from utils import CustomJSONEncoder


class MessageType:
    QUERY_LATEST_BLOCK = 0
    QUERY_BLOCKCHAIN = 1
    RESPONSE_LATEST_BLOCK = 2
    RESPONSE_BLOCKCHAIN = 3
    QUERY_TRANSACTION_TRANSACTIONS = 4
    RESPONSE_TRANSACTIONS = 5
    RESPONSE_TRANSACTION = 6
    CONNECT_MESSAGE = 7


class Message:
    def __init__(self, type: int, data: Any) -> None:
        self.type = type
        self.data = data


sockets = set()
blockchain = None
address = None


def get_sockets():
    return sockets


def get_addr(websocket):
    addr = websocket.remote_address
    addr = f'ws://{addr[0]}:{addr[1]}'
    return addr


async def init_connection(uri):
    if not uri in sockets:
        sockets.add(uri)
        async with websockets.connect(uri) as websocket:
            await write(websocket, connect_message())
            await write(websocket, query_chain_length())


def json_to_object(data):
    try:
        return json.loads(data)
    except:
        return None


def from_json(obj):
    if 'transactions' in obj.keys():
        obj['transactions'] = [Transaction(
            **transaction) for transaction in obj['transactions']]

    if 'chain' in obj.keys():
        chain = obj['chain']
        obj['chain'] = [Block(**block) for block in chain]

    return obj


def blockchain_from_json(obj):
    return json.loads(obj, object_hook=from_json)


async def handler(websocket):
    async for data in websocket:
        message = json_to_object(data)

        if message is None:
            return

        if message['type'] == MessageType.CONNECT_MESSAGE:
            await init_connection(message['data']['address'])
        elif message['type'] == MessageType.QUERY_LATEST_BLOCK:
            broadcast_latest()
        elif message['type'] == MessageType.QUERY_BLOCKCHAIN:
            broadcast_all()
        elif message['type'] == MessageType.RESPONSE_BLOCKCHAIN:
            blockchain_json = json.dumps(message['data'])
            blocks = blockchain_from_json(blockchain_json)

            if blocks is None:
                return

            handle_blockchain_response(blocks['chain'])
        elif message['type'] == MessageType.RESPONSE_TRANSACTION:
            handle_transaction(message['data'])


async def write(websocket, message):
    data = json.dumps(message, cls=CustomJSONEncoder)
    await websocket.send(data)


async def broadcast(message):
    for uri in sockets:
        async with websockets.connect(uri) as websocket:
            await write(websocket, message)


def connect_message():
    data = {
        'address': address
    }
    return Message(type=MessageType.CONNECT_MESSAGE, data=data)


def query_chain_length():
    return Message(type=MessageType.QUERY_LATEST_BLOCK, data=None)


def query_all():
    return Message(type=MessageType.QUERY_BLOCKCHAIN, data=None)


def response_chain():
    return Message(
        type=MessageType.RESPONSE_BLOCKCHAIN,
        data=blockchain
    )


def response_latest():
    data = {
        'chain': [blockchain.last_block]
    }
    return Message(
        type=MessageType.RESPONSE_BLOCKCHAIN,
        data=data
    )


def handle_blockchain_response(blocks: List[Block]):
    if len(blocks) == 0:
        return

    last_block_received = blocks[len(blocks) - 1]
    last_block_held = blockchain.last_block

    if last_block_received.index == 0 and last_block_held.index == 0:
        if last_block_received.timestamp < last_block_held.timestamp:
            blockchain.chain[0] = last_block_received

    if (last_block_received.index > last_block_held.index):
        if last_block_received.previous_hash == last_block_held.hash:
            blockchain.append_block(last_block_received)
        elif len(blocks) == 1:
            exec_async(broadcast(query_all()))
        else:
            blockchain.replace_chain(blocks)


def handle_transaction(data):
    transaction = Transaction(
        sender=data['sender'],
        receiver=data['receiver'],
        amount=data['amount'],
        signature=data['signature']
    )

    blockchain.append_transaction(transaction)


def broadcast_latest():
    exec_async(broadcast(response_latest()))


def broadcast_all():
    exec_async(broadcast(response_chain()))


def broadcast_transaction(transaction):
    message = {
        'type': MessageType.RESPONSE_TRANSACTION,
        'data': transaction
    }
    exec_async(broadcast(message))


def connect_to_peer(uri):
    exec_async(init_connection(uri))


def exec_async(task):
    event_loop = None
    try:
        event_loop = asyncio.get_event_loop()
    except:
        event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    if event_loop.is_running():
        asyncio.ensure_future(task)
    else:
        event_loop.run_until_complete(task)


async def main(port):
    async with websockets.serve(handler, "", port):
        await asyncio.Future()


def init(p2p_port, chain):
    global blockchain
    blockchain = chain
    global address
    address = f'ws://localhost:{p2p_port}'
    print(f'P2P server running on: ws://localhost:{p2p_port}', end='\n\n')
    asyncio.run(main(p2p_port))
