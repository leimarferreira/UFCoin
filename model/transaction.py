class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    @staticmethod
    def validate_transaction(transaction):
        # TODO: Validate the transaction. Validate if both the sender and
        # receiver are valid nodes. If yes, then validate if the sender has the
        # amount to be sent.
        pass
