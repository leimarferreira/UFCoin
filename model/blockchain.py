from numbers import Number
from urllib.parse import urlparse

import requests

from model import Block, Transaction
from model.transaction_pool import get_transaction_pool
from model.wallet import get_public_key_from_wallet, find_unspent_outputs
from network.p2p_server import broadcast_latest, broadcast_transaction_pool
from model.transaction import TransactionInput, TransactionOutput, UnspentTransactionOutput, process_transactions, get_coinbase_transaction
from model.transaction_pool import add_to_transaction_pool, get_transaction_pool, update_transaction_pool
from model.wallet import create_transaction, find_unspent_outputs, get_balance, get_priv_key, get_public_key_from_wallet


class Blockchain:
    def __init__(self):
        self.chain = []
        self.block_generation_inverval = 10000  # in milliseconds
        self.difficult_adjustment_interval = 10  # in blocks
        self.difficult = 4
        self.nodes = set()
        self.mining = False

        # Criar bloco genêsis
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash=None,
            proof=1,
            difficult=self.difficult
        )
        self.chain.append(genesis)
        self.unspent_transactions = []

    def create_block(self, proof: int) -> Block:
        """
        Creates a new block.
        :param proof: <int> Proof of Work of the block to be created.
        :return: <Block> Block created.
        """

        pub_key = get_public_key_from_wallet()
        coinbase_transaction = get_coinbase_transaction(
            pub_key, self.last_block.index + 1)

        last_block = self.last_block
        block = Block(
            index=last_block.index + 1,
            transactions=[coinbase_transaction],
            previous_hash=last_block.hash,
            proof=proof,
            difficult=self.difficult
        )

        return block

    def append_block(self, block: Block) -> bool:
        last_block = self.last_block
        if Block.is_valid_block(block, last_block):
            unspent_outputs = process_transactions(
                block.transactions, self.unspent_transactions, block.index)

            if unspent_outputs == None:
                return False

            self.chain.append(block)
            self.unspent_transactions = unspent_outputs
            broadcast_latest()
            return True

        return False

    def send_transaction(self, address: str, amount: int):
        transaction = create_transaction(address, amount, get_priv_key(),
                                         self.unspent_transactions, get_transaction_pool())

        add_to_transaction_pool(transaction, self.unspent_transactions)
        broadcast_transaction_pool()
        return transaction

    def get_difficult(self):
        if (self.last_block.index % self.difficult_adjustment_interval == 0
                and self.last_block.index != 0):
            self.adjust_difficult()

        return self.difficult

    def adjust_difficult(self):
        previous_adjustment_block = self.chain[-self.difficult_adjustment_interval]
        time_expected = self.block_generation_inverval * \
            self.difficult_adjustment_interval
        time_taken = self.last_block.timestamp - previous_adjustment_block.timestamp

        if time_taken < time_expected / 2:
            self.difficult += 1
        elif time_taken > time_expected * 2:
            self.difficult -= 1

    @staticmethod
    def get_accumulated_difficult(chain):
        return sum([2 ** block.difficult for block in chain])

    def validate_hash(self, block: Block) -> bool:
        """
        Validates if the block hash has a leading quantity of zeroes, where the
        quantity is determined by the current difficult.
        """
        difficult = self.get_difficult()
        return block.hash[:difficult] == "0" * difficult

    def find_block(self) -> Block:
        """
        Proof of Work algorithm. Try to find a block whose hash matches the
        current difficult.
        :return: <Block> Block found.
        """

        proof = 0
        block = self.create_block(proof)
        while self.validate_hash(block) is False:
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

    def is_chain_valid(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if not Block.is_valid_block(block, last_block):
                return False

            last_block = block
            current_index += 1

        return True

    def replace_chain(self, chain):
        if self.is_chain_valid(chain) and self.get_accumulated_difficult(chain) > self.get_accumulated_difficult(self.chain):
            self.chain = chain

    def resolve_conflicts(self):

        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json(object_hook=self.__from_json)['chain']

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def get_unspent_transactions(self):
        return find_unspent_outputs(get_public_key_from_wallet(), self.get_unspent_transactions())

    def get_account_balance(self):
        print(self.unspent_transactions)
        pub_key = get_public_key_from_wallet()
        result = get_balance(pub_key, self.unspent_transactions)
        return result

    def handle_received_transaction(self, transaction):
        add_to_transaction_pool(transaction, self.unspent_transactions)

    @staticmethod
    def __from_json(obj):
        if 'transactions' in obj.keys():
            obj['transactions'] = [Transaction(
                **transaction) for transaction in obj['transactions']]

        if 'chain' in obj.keys():
            chain = obj['chain']
            obj['chain'] = [Block(**block) for block in chain]

        return obj

    @property
    def last_block(self) -> Block:
        return self.chain[-1]
