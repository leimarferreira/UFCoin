import time
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


def find_last_transaction_by_user(address, transactions):
    if transactions is None or len(transactions) == 0:
        return None

    last_transaction = None
    for transaction in transactions:
        if transaction.sender == address:
            if last_transaction == None or transaction.timestamp > last_transaction.timestamp:
                last_transaction = transaction

    return last_transaction


def create_transaction(receiver_addr, my_addr, amount, transactions):
    last_transaction = find_last_transaction_by_user(my_addr, transactions)

    current_time = time.time()

    if last_transaction is not None:
        diff = current_time - last_transaction.timestamp
        if diff < 600:  # 600 segundos ou 10 minutos
            time_left = time.strftime("%M:%S", time.gmtime(600 - diff))
            message = f'Usuários só podem realizar uma transação a cada 10 minutos. ' \
                f'Próxima transação pode ser realizada em {time_left}'
            raise RuntimeError(message)

    balance = get_balance(my_addr, transactions)

    if balance < amount:
        raise RuntimeError("Saldo menor que a quantidade enviada.")

    transaction = build_transaction(my_addr, receiver_addr, amount)

    return transaction
