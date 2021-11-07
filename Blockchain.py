import sys
import time
from hashlib import sha256
from random import seed, randint


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # minerar o primeiro bloco da cadeia
        self.create_block(previous_hash="0", proof=1)

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

    def proof_of_work(self, last_proof):
        seed()
        proof = randint(0, sys.maxsize)
        while self.validate_proof(last_proof, proof) is False:
            proof = randint(0, sys.maxsize)

        return proof

    @staticmethod
    def validate_proof(last_proof, proof):
        number_of_zeroes = 5
        hash = sha256(str(proof * last_proof).encode()).hexdigest()
        return hash[:5] == "0" * number_of_zeroes
