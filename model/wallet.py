import rsa
import os
from model.transaction import create_transaction as build_transaction
import re
import sys
import random

PRIV_KEY_PATH = f'../wallet/privatekey{random.randint(0, sys.maxsize)}'


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


def get_public_key() -> str:
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


def get_pub_key_from_priv_key(priv_key):
    priv_key = rsa.PrivateKey.load_pkcs1(bytes.fromhex(priv_key), "DER")
    pub_key = rsa.PublicKey(priv_key.n, priv_key.e)
    return pub_key.save_pkcs1("DER").hex()


def get_balance(address: str, transactions):
    received_amount = 0
    sent_amount = 0
    for transaction in transactions:
        if transaction.sender == address:
            sent_amount += transaction.amount
        elif transaction.receiver == address:
            received_amount += transaction.amount

    balance = received_amount - sent_amount
    return balance


def create_transaction(receiver_addr, amount, priv_key, transactions):
    my_addr = get_pub_key_from_priv_key(priv_key)

    balance = get_balance(my_addr, transactions)

    if balance < amount:
        return None

    transaction = build_transaction(priv_key, my_addr, receiver_addr, amount)

    return transaction
