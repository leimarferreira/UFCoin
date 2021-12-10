import time
from hashlib import sha256
from typing import Any, List

from model.transaction import Transaction


class Block:
    def __init__(self, index: int, transactions: List[Transaction], previous_hash: str, proof: int):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.proof = proof
        self.hash = self.hash_block(self)

    @staticmethod
    def hash_block(block: 'Block') -> str:
        """
        Hash a block.
        :param block: <Block> The block to be hashed.
        :return: <str> The hash of the block.
        """

        encoded_block = f'{block.index}{block.timestamp}{block.transactions}' \
            f'{block.previous_hash}{block.proof}'.encode()

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

        if block.index != previous_block.index + 1:
            return False

        if block.previous_hash != previous_block.hash:
            return False

        if Block.hash_block(block) != block.hash:
            return False

        return True
