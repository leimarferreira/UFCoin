import sys
import time
import json
from hashlib import sha256
from random import seed, randint

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.create_block(previous_hash="0", proof=1)# minerar o primeiro block da cadeia

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
        print("computing1...")
        seed()
        proof = randint(0, 100)
        print("computing2...")
        while self.validate_proof(last_proof, proof) is False:
            proof = randint(0, sys.maxsize)

        return proof

    @staticmethod
    def validate_proof(last_proof, proof):
        number_of_zeroes = 5
        hash = sha256(str(proof * last_proof).encode()).hexdigest()
        return hash[:5] == "0" * number_of_zeroes

    def lenght(self):
        return len(self.chain)

    def previous_block(self):
        return self.chain[self.lenght() -1]

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return sha256(encoded_block).hexdigest()




    