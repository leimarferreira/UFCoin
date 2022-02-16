from copy import deepcopy
from hashlib import sha256
import os
import pickle

from network.p2p_server import (broadcast_latest, broadcast_transaction, broadcast_difficult,
                                connect_to_peer)

from model import Block, Transaction
from model.transaction import Transaction, get_coinbase_transaction
from model.wallet import create_transaction, get_balance, get_identifier

BLOCKCHAIN_PATH = './blockchain/'


class Blockchain:
    def __init__(self):
        self.chain = []
        self.block_generation_inverval = 10  # in seconds
        self.difficult_adjustment_interval = 10  # in blocks
        self.difficult = 5
        self.nodes = set()
        self.peer_addresses = set()
        self.mining = False

        # Criar bloco genêsis
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash='',
            proof=1,
            difficult=self.difficult
        )
        self.chain.append(genesis)
        self.transaction_pool = []

    def create_block(self, proof: int) -> Block:
        """
        Creates a new block.
        :param proof: <int> Proof of Work of the block to be created.
        :return: <Block> Block created.
        """

        address = get_identifier()
        coinbase_transaction = get_coinbase_transaction(
            address)

        transactions = [coinbase_transaction]
        transactions.extend(self.transaction_pool)

        last_block = self.last_block
        block = Block(
            index=last_block.index + 1,
            transactions=transactions,
            previous_hash=last_block.hash,
            proof=proof,
            difficult=self.difficult
        )

        return block

    def append_block(self, block: Block) -> bool:
        last_block = self.last_block
        if Block.is_valid_block(block, last_block):
            self.chain.append(block)
            self.transaction_pool = []
            broadcast_latest()
            self.save_blockchain(self, get_identifier())
            return True

        return False

    def append_transaction(self, transaction):
        self.transaction_pool.append(transaction)
        self.save_blockchain(self, get_identifier())

    def send_transaction(self, address: str, amount: int):
        transactions = self.get_all_transactions()
        transaction = create_transaction(
            address, get_identifier(), amount, transactions)

        if transaction is None:
            return None

        if not self.is_valid_node(address):
            raise RuntimeError("Destinatário não incluso na rede.")

        self.append_transaction(transaction)
        broadcast_transaction(transaction)
        return transaction

    def register_node(self, address):
        connect_to_peer(address)

    def get_nodes(self):
        return self.nodes

    def is_valid_node(self, address):
        return address in self.peer_addresses

    def get_difficult(self):
        if (self.last_block.index % self.difficult_adjustment_interval == 0
                and self.last_block.index != 0
                and self.last_block.difficult == self.difficult):
            self.adjust_difficult()

        return self.difficult

    def adjust_difficult(self):
        previous_adjustment_block = self.chain[-self.difficult_adjustment_interval]

        time_expected = self.block_generation_inverval * \
            self.difficult_adjustment_interval
        time_taken = self.last_block.timestamp - previous_adjustment_block.timestamp

        if time_taken < time_expected:
            self.difficult += 1
        elif time_taken > time_expected:
            self.difficult -= 1

        broadcast_difficult(self.difficult)
        self.save_blockchain(self, get_identifier())

    @staticmethod
    def get_accumulated_difficult(chain):
        return sum([2 ** block.difficult for block in chain])

    def validate_proof(self, proof, last_proof):
        hash = sha256(f'{proof * last_proof}'.encode()).hexdigest()
        difficult = self.get_difficult()
        return hash[:difficult] == "0" * difficult

    def find_block(self) -> Block:
        """
        Proof of Work algorithm. Try to find a block whose hash matches the
        current difficult.
        :return: <Block> Block found.
        """

        proof = self.last_block.proof + 1
        while self.validate_proof(proof, self.last_block.proof) is False:
            proof += 1

        block = self.create_block(proof)
        return block

    def mine(self):
        if self.mining:
            return

        self.mining = True

        while self.mining:
            block = self.find_block()
            self.append_block(block)

    def stop_mining(self):
        self.mining = False

    def is_blockchain_valid(self, blockchain):
        chain = blockchain.chain
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if not Block.is_valid_block(block, last_block):
                return False

            last_block = block
            current_index += 1

        return True

    def replace_blockchain(self, blockchain):
        if blockchain is None:
            return

        current_nodes = list(self.nodes)

        if self.is_blockchain_valid(blockchain) and self.get_accumulated_difficult(blockchain.chain) > self.get_accumulated_difficult(self.chain):
            self.chain = blockchain.chain
            self.block_generation_inverval = blockchain.block_generation_inverval
            self.difficult_adjustment_interval = blockchain.difficult_adjustment_interval
            self.difficult = blockchain.difficult
            nodes = list(blockchain.nodes)
            nodes.extend(current_nodes)
            self.nodes = set(nodes)
            self.peer_addresses = blockchain.peer_addresses
            self.transaction_pool = blockchain.transaction_pool

            self.save_blockchain(self, get_identifier())

        for node in deepcopy(list(self.nodes)):
            self.register_node(node)

    def get_account_balance(self):
        address = get_identifier()
        transactions = self.get_all_transactions()

        result = get_balance(address, transactions)
        return result

    def get_all_transactions(self):
        transactions = []
        for block in self.chain:
            transactions.extend(block.transactions)

        transactions.extend(self.transaction_pool)

        return transactions

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    @staticmethod
    def from_dict(bcdict):
        blockchain = Blockchain()
        blockchain.block_generation_inverval = bcdict['block_generation_inverval']
        blockchain.difficult_adjustment_interval = bcdict['difficult_adjustment_interval']
        blockchain.difficult = bcdict['difficult']
        blockchain.nodes = set(bcdict['nodes'])
        blockchain.peer_addresses = set(bcdict['peer_addresses'])
        blockchain.mining = False
        blockchain.chain = [Block.from_dict(bdict)
                            for bdict in bcdict['chain']]
        blockchain.transaction_pool = [Transaction.from_dict(
            tr) for tr in bcdict['transaction_pool']]

        return blockchain

    @staticmethod
    def save_blockchain(blockchain, node_identifier):
        path = f'{BLOCKCHAIN_PATH}{node_identifier}'

        if not os.path.exists(path):
            os.makedirs(path)

        file = f'{path}/chain'
        with open(file, 'wb') as blockchain_file:
            pickle.dump(blockchain, blockchain_file)

    @staticmethod
    def load_blockchain(node_identifier):
        file = f'{BLOCKCHAIN_PATH}{node_identifier}/chain'
        try:
            with open(file, 'rb') as blockchain_file:
                return pickle.load(blockchain_file)
        except:
            return None
