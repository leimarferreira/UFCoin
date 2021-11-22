import sys
import time
import json
from hashlib import sha256
from random import seed, randint

# TODO: Add docstring comments in all the functions.


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # minerar o primeiro bloco da cadeia
        self.create_block(previous_hash=None, proof=self.get_proof())

    def create_block(self, previous_hash, proof):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.current_transactions,
            "previous_hash": previous_hash,
            "proof": proof
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender, receiver, amount):
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

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        Proof of Work algorithm.
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

    @staticmethod
    def hash_block(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return sha256(encoded_block).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]
