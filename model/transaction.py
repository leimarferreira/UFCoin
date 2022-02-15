from hashlib import sha256
import rsa


class Transaction:
    def __init__(self, sender, receiver, amount, signature=None) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature


COINBASE_AMOUNT = 5


def get_coinbase_transaction(receiver):
    return Transaction('', receiver, COINBASE_AMOUNT)


def create_transaction(sender_addr, receiver_addr, amount):
    transaction = Transaction(sender_addr, receiver_addr, amount)
    # FIXME: sign_transaction(transaction, sender_priv_key)
    return transaction


def hash_transaction(transaction):
    content = f'{transaction.sender}{transaction.receiver}{transaction.amount}'
    hash = sha256(content.encode()).hexdigest()
    return hash


def sign_transaction(transaction, sender_priv_key):
    hash = hash_transaction(transaction)
    priv_key = rsa.PrivateKey.load_pkcs1(bytes.fromhex(sender_priv_key), "DER")
    signature = rsa.sign(bytes(hash, encoding='utf-8'),
                         priv_key, 'SHA-256').hex()
    transaction.signature = signature


def is_valid_transaction(transaction):
    pub_key = rsa.PublicKey.load_pkcs1(
        bytes.fromhex(transaction.sender), 'DER')
    hash = hash_transaction(transaction)
    try:
        rsa.verify(bytes(hash, encoding='utf-8'),
                   bytes.fromhex(transaction.signature), pub_key)
        return True
    except:
        return False
