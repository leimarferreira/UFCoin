from model.transaction import create_transaction as build_transaction
from hashlib import sha512


def init_wallet(user, passwd):
    generate_identifier(user, passwd)


def generate_identifier(user, passwd):
    global identifier
    content = f'{user}{passwd}'.encode()
    identifier = sha512(content).hexdigest()


def get_identifier():
    global identifier
    return identifier


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


def create_transaction(receiver_addr, my_addr, amount, transactions):
    balance = get_balance(my_addr, transactions)

    if balance < amount:
        raise RuntimeError("Saldo menor que a quantidade enviada.")

    transaction = build_transaction(my_addr, receiver_addr, amount)

    return transaction
