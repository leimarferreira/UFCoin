import rsa
import os
from model.transaction import Transaction, TransactionInput, TransactionOutput, UnspentTransactionOutput, get_id, get_public_key, sign_input
from typing import List
import re

PRIV_KEY_PATH = '../wallet/privatekey'


def generate_private_key():
    poolsize = os.cpu_count()
    (_, priv_key) = rsa.newkeys(1024, poolsize=poolsize)

    path = re.sub('^(.[^/]+){1}', '', PRIV_KEY_PATH[::-1])[::-1]
    if not os.path.exists(path):
        os.mkdir(path)

    with open(PRIV_KEY_PATH, 'w') as priv_key_file:
        priv_key_file.write(priv_key.save_pkcs1("DER").hex())


def init_wallet():
    try:
        file = open(PRIV_KEY_PATH, 'r')
        file.close()
    except FileNotFoundError:
        generate_private_key()


def get_public_key_from_wallet():
    pub_key = None
    try:
        priv_key_file = open(PRIV_KEY_PATH, 'r')
        priv_key_der = priv_key_file.read()
        priv_key = rsa.PrivateKey.load_pkcs1(
            bytes.fromhex(priv_key_der), "DER")
        pub_key = rsa.PublicKey(priv_key.n, priv_key.e).save_pkcs1("DER").hex()
    except:
        pass

    return pub_key


def get_priv_key():
    try:
        file = open(PRIV_KEY_PATH, 'r')
        return file.read()
    except FileNotFoundError:
        return None


def get_balance(address: str, unspent_outputs: List[UnspentTransactionOutput]):
    balance = 0
    for output in unspent_outputs:
        if output.address == address:
            balance += output.amount

    return balance


def find_outputs_for_amount(amount, ouputs: List[UnspentTransactionOutput]):
    current_amount = 0
    included_unspent_outputs = []
    for unspent_output in ouputs:
        included_unspent_outputs.append(unspent_output)
        current_amount += unspent_output.amount

        if current_amount >= amount:
            leftover_amount = current_amount - amount
            return (included_unspent_outputs, leftover_amount)

    raise RuntimeError("Not enough coins to send transaction.")


def create_outputs(receiver_addr, my_addr, amount, leftover_amount):
    output = TransactionOutput(receiver_addr, amount)
    if leftover_amount == 0:
        return [output]

    leftover_transaction = TransactionOutput(my_addr, leftover_amount)
    return [output, leftover_transaction]


def create_transaction(receiver_addr, amount, priv_key, unspent_outputs):
    my_addr = get_public_key(priv_key)

    my_unspent_outputs = []
    for unspent_output in unspent_outputs:
        if unspent_output.address == my_addr:
            my_unspent_outputs.append(unspent_output)

    included_unspent_outputs, leftover_amount = find_outputs_for_amount(
        amount, my_unspent_outputs)

    unsigned_inputs = []
    for output in included_unspent_outputs:
        input = TransactionInput(output.output_id, output.output_index, '')
        unsigned_inputs.append(input)

    outputs = create_outputs(receiver_addr, my_addr, amount, leftover_amount)
    transaction = Transaction(None, unsigned_inputs, outputs)
    transaction.id = get_id(transaction)

    for i in range(len(transaction.inputs)):
        input = transaction.inputs[i]
        input.signature = sign_input(transaction, i, priv_key, unspent_output)
        transaction.inputs[i] = input

    return transaction
