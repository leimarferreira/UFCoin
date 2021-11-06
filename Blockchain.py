import datetime
import requests
import json

class Blockchain:
    def __init__(self):
        chain = []
        self.create_block(previous="0", proof=1)# minerar o primeiro block da cadeia

    def create_block(self, previous, proof):
        block = {
            "index" : len(self.chain),
            "time" : str(datetime.datetime.now()),
            "previous_hash" : previous,
            "proof" : proof
        }

        self.chain.append(block)
        return block