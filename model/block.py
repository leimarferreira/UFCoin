import time
from hashlib import sha256
from typing import Any, List

from model.transaction import Transaction


class Block:
    def __init__(
            self,
            index: int,
            transactions: List[Transaction],
            proof: int,
            difficult: int,
            previous_hash: str,
            hash: str = None,
            timestamp: float = None):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.proof = proof
        self.difficult = difficult
        self.previous_hash = previous_hash
        self.hash = hash if hash is not None else self.hash_block(self)

    @staticmethod
    def hash_block(block: 'Block') -> str:
        """
        Hash a block.
        :param block: <Block> The block to be hashed.
        :return: <str> The hash of the block.
        """

        encoded_block = f'{block.index}{block.timestamp}{block.transactions}' \
            f'{block.proof}{block.difficult}{block.previous_hash}'.encode()

        return sha256(encoded_block).hexdigest()

    @staticmethod
    def is_valid_block(block: 'Block', previous_block: 'Block') -> bool:
        """
        Checks if a block is valid.
        :param block: <Block> The block to be validated.
        :param previous_block: <Block> The block preceding the block being
        validated in the chain.
        :return: <bool> True if the block is valid, False otherwise.
        """

        if block is None or previous_block is None:
            return False

        if block.index != previous_block.index + 1:
            return False

        if block.previous_hash != previous_block.hash:
            return False

        if Block.hash_block(block) != block.hash:
            return False

        return True

    def __str__(self) -> str:
        return f'{{ index: {self.index}, timestamp: {self.timestamp}, ' \
            f'transactions: {self.transactions}, ' \
            f'proof: {self.proof}, difficult: {self.difficult}, ' \
            f'previous_hash: {self.previous_hash}, '\
            f'hash: {self.hash} }}'

    def __repr__(self) -> str:
        return self.__str__()
