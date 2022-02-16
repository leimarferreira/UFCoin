import asyncio
from copy import deepcopy
import json
from typing import Any

import websockets
from model import Block
from model.transaction import Transaction
from model.wallet import get_identifier
from utils import CustomJSONEncoder


class MessageType:
    QUERY_LATEST_BLOCK = 0
    QUERY_BLOCKCHAIN = 1
    RESPONSE_LATEST_BLOCK = 2
    RESPONSE_BLOCKCHAIN = 3
    RESPONSE_TRANSACTIONS = 4
    RESPONSE_TRANSACTION = 5
    CONNECT_MESSAGE = 6
    DIFFICULT = 5


class Message:
    def __init__(self, type: int, data: Any) -> None:
        self.type = type
        self.data = data


sockets = set()
address = None


def get_sockets():
    return sockets


def get_addr(websocket):
    addr = websocket.remote_address
    addr = f'ws://{addr[0]}:{addr[1]}'
    return addr


async def init_connection(uri):
    global address

    if uri == address:
        blockchain.nodes.remove(uri)
        update_blockchain_nodes()

    if not uri in sockets and uri != address:
        sockets.add(uri)
        try:
            async with websockets.connect(uri) as websocket:
                await write(websocket, connect_message())
                await write(websocket, query_chain_length())
        except:
            sockets.remove(uri)

        update_blockchain_nodes()
        


def update_blockchain_nodes():
    blockchain.nodes = sockets
    blockchain.save_blockchain(blockchain, get_identifier())


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
            await handle_connection(message['data'])
        elif message['type'] == MessageType.QUERY_LATEST_BLOCK:
            broadcast_latest()
        elif message['type'] == MessageType.QUERY_BLOCKCHAIN:
            broadcast_all()
        elif message['type'] == MessageType.RESPONSE_LATEST_BLOCK:
            handle_latest_block(message['data'])
        elif message['type'] == MessageType.RESPONSE_BLOCKCHAIN:
            handle_blockchain_response(message['data'])
        elif message['type'] == MessageType.RESPONSE_TRANSACTION:
            handle_transaction(message['data'])
        elif message['type'] == MessageType.DIFFICULT:
            handle_difficult_change(message['data'])


async def write(websocket, message):
    data = json.dumps(message, cls=CustomJSONEncoder)
    await websocket.send(data)


async def broadcast(message):
    uris = deepcopy(list(sockets))
    for uri in uris:
        try:
            async with websockets.connect(uri) as websocket:
                await write(websocket, message)
        except:
            sockets.remove(uri)


def connect_message():
    data = {
        'address': address,
        'identifier': get_identifier()
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
    return Message(
        type=MessageType.RESPONSE_LATEST_BLOCK,
        data=blockchain.last_block
    )


async def handle_connection(data):
    await init_connection(data['address'])
    blockchain.peer_addresses.add(data['identifier'])


def handle_blockchain_response(bcdict):
    global blockchain
    chain = blockchain.from_dict(bcdict)
    blockchain.replace_blockchain(chain)


def handle_latest_block(block_dict):
    block = Block.from_dict(block_dict)
    last_block = blockchain.last_block

    if block.index == last_block.index and block.hash == last_block.hash:
        return
    elif block.index == last_block.index + 1 and block.previous_hash == last_block.hash:
        blockchain.append_block(block)
    else:
        exec_async(broadcast(query_all()))


def handle_transaction(data):
    transaction = Transaction.from_dict(data)

    blockchain.append_transaction(transaction)


def handle_difficult_change(difficult):
    blockchain.difficult = difficult


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


def broadcast_difficult(difficult):
    message = {
        'type': MessageType.DIFFICULT,
        'data': difficult
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


async def main(ip, port):
    async with websockets.serve(handler, ip, port, close_timeout=60):
        await asyncio.Future()


def init(ip, p2p_port, chain):
    global blockchain
    blockchain = chain
    global address
    address = f'ws://{ip}:{p2p_port}'
    print(f'P2P server running on: {address}', end='\n\n')
    asyncio.run(main(ip, p2p_port))


blockchain: Any = None
