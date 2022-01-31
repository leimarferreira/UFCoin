import asyncio
from cgitb import handler
import json
from urllib.parse import urlparse
from typing import Any, List

import websockets
from model import Block, Blockchain, blockchain
from model.transaction_pool import get_transaction_pool
from utils import CustomJSONEncoder


class MessageType:
    QUERY_LATEST_BLOCK = 0
    QUERY_FULL_BLOCKCHAIN = 1
    RESPONSE_LATEST_BLOCK = 2
    RESPONSE_FULL_BLOCKCHAIN = 3
    QUERY_TRANSACTION_POOL = 4
    RESPONSE_TRANSACTION_POOL = 5


class Message:
    def __init__(self, type: int, data: Any) -> None:
        self.type = type
        self.data = data


sockets = set()
blockchain: Blockchain = None


def get_sockets():
    return sockets


async def init_connection(websocket):
    sockets.add(websocket)
    await write(websocket, query_chain_length())


def json_to_object(data):
    try:
        return json.loads(data, cls=CustomJSONEncoder)
    except:
        return None


async def handler(websocket):
    await init_connection(websocket)
    async for data in websocket:
        message = json_to_object(data)

        if message is None:
            print('Erro. Não foi possível decodificar o JSON.')
            return

        if message.type == MessageType.QUERY_LATEST_BLOCK:
            await write(websocket, response_latest())
        elif message.type == MessageType.QUERY_FULL_BLOCKCHAIN:
            await write(websocket, response_chain)
        elif message.type == MessageType.RESPONSE_FULL_BLOCKCHAIN:
            blocks = json_to_object(message.data)

            if blocks is None:
                return

            await handle_blockchain_response(blocks)
        elif message.type == MessageType.QUERY_TRANSACTION_POOL:
            await write(websocket, response_transaction_pool())
        elif message.type == MessageType.RESPONSE_TRANSACTION_POOL:
            transactions = json_to_object(message.data)

            if transactions is None:
                return

            for transaction in transactions:
                try:
                    handle_received_transaction(transaction)
                    await broadcast_transaction_pool()
                except:
                    pass


async def write(websocket, message):
    await websocket.send(json.dumps(message))


async def broadcast(message):
    for socket in sockets:
        await write(socket, message)


def query_chain_length():
    return Message(type=MessageType.QUERY_LATEST_BLOCK, data=None)


def query_all():
    return Message(type=MessageType.QUERY_FULL_BLOCKCHAIN, data=None)


def response_chain():
    return Message(
        type=MessageType.RESPONSE_FULL_BLOCKCHAIN,
        data=json.dumps(blockchain.chain))


def response_latest():
    return Message(
        type=MessageType.RESPONSE_LATEST_BLOCK,
        data=json.dumps(blockchain.last_block))


def query_transaction_pool():
    return Message(type=MessageType.QUERY_TRANSACTION_POOL, data=None)


def response_transaction_pool():
    return Message(
        type=MessageType.RESPONSE_TRANSACTION_POOL,
        data=json.dumps(get_transaction_pool())
    )


async def handle_blockchain_response(blocks: List[Block]):
    if len(blocks) == 0:
        return

    last_block_received = blocks[len(blocks) - 1]
    last_block_held = blockchain.last_block

    if (last_block_received.index > last_block_held.index):
        if last_block_received.previous_hash == last_block_held.hash:
            blockchain.append_block(last_block_received)
        elif len(blocks) == 1:
            await broadcast(query_all())
        else:
            blockchain.replace_chain(blocks)


async def broadcast_latest():
    await broadcast(response_latest())


async def connect_to_peer(uri):
    async with websockets.connect(uri) as websocket:
        await init_connection(websocket)


async def broadcast_transaction_pool():
    await broadcast(response_transaction_pool())


async def main():
    async with websockets.serve(handler, "", 6000):
        await asyncio.Future()


def init(chain: Blockchain):
    global blockchain
    blockchain = chain
    asyncio.run(main())
