import json
import sys
from hashlib import sha256
from random import randint, seed
from urllib.parse import urlparse

from model.block import Block

# TODO: Add docstring comments in all the functions.


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Criar bloco genêsis
        genesis = Block(0, [], None, self.get_proof())
        self.chain.append(genesis)

    def create_block(self, proof: int) -> Block:
        """
        Creates a new block.
        :param proof: <int> Proof of Work of the block to be created.
        :return: <Block> Block created.
        """

        last_block = self.last_block
        block = Block(index=last_block.index + 1, transactions=self.current_transactions,
                      previous_hash=last_block.hash, proof=proof)

        if not Block.is_valid_block(block, last_block):
            return None

        self.current_transactions = []
        self.chain.append(block)

        return block

    def create_transaction(self, sender, receiver, amount):
        """
        Creates a new transaction.
        :param sender: <str> The address of the sender node.
        :param receiver: <str> The addres of the receiver node.
        :param amount: <int> Amount of cryptocurrencies to be sent.
        :return: <int> The index of the block which the transaction will be
        added to i.e. the next block to be mined.
        """

        # TODO: Validate the transaction. Validate if both the sender and
        # receiver are valid nodes. If yes, then validate if the sender has the
        # amount to be sent.

        self.current_transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })

        return self.last_block.index + 1

    # TODO: implement a better proof of work
    def proof_of_work(self, last_proof):
        """
        Proof of Work algorithm.
        - Find a number x such that hash(x * y) has 5 leading zeroes.
        - x is the current proof and y is the proof of the previous block. 
        :param last_proof: <int> Proof of Work of the last block mined.
        :return: <int> Proof of Work of the current block.
        """

        proof = self.get_proof()
        while self.validate_proof(last_proof, proof) is False:
            proof = self.get_proof()

        return proof

    @staticmethod
    def get_proof():
        """
        Get a proof value.
        :return: <int> Random generated value.
        """

        seed()
        return randint(1, sys.maxsize)

    @staticmethod
    def validate_proof(last_proof, proof):
        """
        Validates if the hash of proof * last proof contains at least 5 leading
        zeroes.
        :param last_proof: <int> Proof of the previous block.
        :param proof: <int> Current proof.
        :return: <bool> True if the condition is met, otherwise False.
        """

        number_of_zeroes = 5
        hash = sha256(str(proof * last_proof).encode()).hexdigest()
        return hash[:5] == "0" * number_of_zeroes

    def is_chain_valid(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if not Block.is_valid_block(block, last_block):
                return False

            if not self.validate_proof(last_block.proof, block.proof):
                return False

            last_block = block
            current_index += 1

        return True

    def replace_chain(self, new_chain):
        # TODO: replace the chain if the chain is invalid
        pass

    @property
    def last_block(self):
        return self.chain[-1]
