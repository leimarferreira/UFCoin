import time

class Transaction:
    def __init__(self, sender, receiver, amount, timestamp=None) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp if timestamp is not None else time.time()

    @staticmethod
    def from_dict(trdict):
        transaction = Transaction(
            sender=trdict['sender'],
            receiver=trdict['receiver'],
            amount=trdict['amount'],
            timestamp=trdict['timestamp']
        )

        return transaction


COINBASE_AMOUNT = 5


def get_coinbase_transaction(receiver):
    return Transaction('0', receiver, COINBASE_AMOUNT)


def create_transaction(sender_addr, receiver_addr, amount):
    transaction = Transaction(sender_addr, receiver_addr, amount)
    return transaction
