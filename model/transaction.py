from typing import List
from functools import reduce
from hashlib import sha256
import rsa

COINBASE_AMOUNT = 5


class TransactionOutput:
    def __init__(self, address: str, amount: int) -> None:
        self.address = address
        self.amount = amount

    def __str__(self) -> str:
        return f'{self.address}{self.amount}'


class TransactionInput:
    def __init__(
            self,
            output_id: str,
            output_index: int,
            signature: str) -> None:
        self.output_id = output_id
        self.output_index = output_index
        self.signature = signature

    def __str__(self) -> str:
        return f'{self.output_id}{self.output_index}'


class UnspentTransactionOutput:
    def __init__(self, output_id, output_index, address, amount) -> None:
        self.output_id = output_id
        self.output_index = output_index
        self.address = address
        self.amount = amount


class Transaction:

    def __init__(self, id: str, inputs: List[TransactionInput],
                 outputs: List[TransactionOutput]) -> None:
        self.id = id
        self.inputs = inputs
        self.outputs = outputs


def get_id(transaction: Transaction) -> str:
    inputs_content = reduce(lambda x, y: f"{x}{y}", transaction.inputs)
    outputs_content = reduce(lambda x, y: f"{x}{y}", transaction.outputs)

    return sha256(f"{inputs_content}{outputs_content}".encode()).hexdigest()


def find_unspent_output(transaction_id, index,
                        unspent_outputs: List[UnspentTransactionOutput]):

    for output in unspent_outputs:
        if output.output_id == transaction_id and output.output_index == index:
            return output

    return None


def validate_input(
    input: TransactionInput,
    transaction: Transaction,
    unspent_transactions: List[UnspentTransactionOutput],
):
    output = None
    for item in unspent_transactions:
        if (item.output_id == input.output_id
                and item.output_index == input.output_index):
            output = item
            break

    if output is None:
        return False

    address = output.address
    key = rsa.PublicKey.load_pkcs1(bytes.fromhex(address), "DER")

    try:
        rsa.verify(bytes.fromhex(transaction.id),
                   bytes.fromhex(input.signature), key)
        return True
    except:
        return False


def validate_transaction(transaction: Transaction,
                         unspent_outputs: List[UnspentTransactionOutput]):
    if get_id(transaction) != transaction.id:
        return False

    for input in transaction.inputs:
        if not validate_input(input, transaction, unspent_outputs):
            return False

    total_input_values = 0
    for input in transaction.inputs:
        total_input_values += get_inputs_amount(input)

    total_output_values = 0
    for output in transaction.outputs:
        total_output_values += output.amount

    if total_output_values != total_input_values:
        return False

    return True


def validate_block_transactions(
    transactions: List[Transaction],
    unspent_outputs: List[UnspentTransactionOutput],
    block_index: int,
):
    coinbase_transaction = transactions[0]

    if not validate_coinbase_transaction(coinbase_transaction, block_index):
        return False

    inputs = []
    for transaction in transactions:
        inputs.extend(transaction.inputs)

    if has_duplicates(inputs):
        return False

    for transaction in transactions:
        if not validate_transaction(transaction, unspent_outputs):
            return False


def has_duplicates(inputs: List[TransactionInput]):
    inputs_dict = dict()
    for input in inputs:
        existing_input = inputs_dict.get(input.signature)
        if (existing_input is not None
                and input.output_id == existing_input.output_id
                and input.output_index == existing_input.output_index):
            return True

        inputs_dict.setdefault(input.signature, input)

    return False


def validate_coinbase_transaction(transaction: Transaction, block_index: int):
    if transaction is None:
        return False

    if get_id(transaction) != transaction.id:
        return False

    if len(transaction.inputs) != 1:
        return False

    if transaction.inputs[0].output_index != block_index:
        return False

    if len(transaction.outputs) != 1:
        return False

    if transaction.outputs[0].amount != COINBASE_AMOUNT:
        return False

    return True


def get_inputs_amount(input: TransactionInput,
                      unspent_outputs: List[UnspentTransactionOutput]):
    return find_unspent_output(
        input.output_id,
        input.output_index,
        unspent_outputs).amount


def get_coinbase_transaction(address: str, block_index: int):
    input = TransactionInput("", block_index, "")
    transaction = Transaction(
        "",
        [input],
        [TransactionOutput(address, COINBASE_AMOUNT)]
    )
    transaction.id = get_id(transaction)

    return transaction


def sign_input(
        transaction: "Transaction",
        input_index,
        priv_key,
        unspent_outputs):
    input = transaction.inputs[input_index]
    data_to_sign = transaction.id
    unspent_output = find_unspent_output(
        input.output_id, input.output_index, unspent_outputs)

    if unspent_output is None:
        raise RuntimeError("Could not find referenced transaction output.")

    address = unspent_output.address

    if address != get_public_key(priv_key):
        raise RuntimeError(
            "Private key doesn't match address reference by input.")

    key = rsa.PrivateKey.load_pkcs1(bytes.fromhex(priv_key), "DER")
    signature = rsa.sign(data_to_sign.encode(), key, 'SHA-256').hex()

    return signature


def update_unspent_transaction_outputs(
    new_transactions: List["Transaction"],
    unspent_transaction_outputs: List[UnspentTransactionOutput],
):
    new_unspent_transactions = []

    for transaction in new_transactions:
        outputs = transaction.outputs

        for i in range(len(outputs)):
            new_unspent_transactions.append(
                UnspentTransactionOutput(transaction.id, i,
                                         outputs[i].address,
                                         outputs[i].amount))

    consumed_outputs = []
    for transaction in new_transactions:
        inputs = transaction.inputs

        for input in inputs:
            consumed_outputs.append(
                UnspentTransactionOutput(input.output_id,
                                         input.output_index, "", 0))

    resulting_unspent_outputs = []
    for output in unspent_transaction_outputs:
        if not find_unspent_output(output.output_id, output.output_index,
                                   consumed_outputs):
            resulting_unspent_outputs.append(output)

    return resulting_unspent_outputs


def process_transactions(
        transactions: List[Transaction],
        unspent_outputs,
        block_index):
    if not is_valid_transactions_structure(transactions):
        return None

    if not validate_block_transactions(
            transactions, unspent_outputs, block_index):
        return None

    return update_unspent_transaction_outputs(transactions, unspent_outputs)


def get_public_key(private_key):
    priv_key = rsa.PrivateKey.load_pkcs1(bytes.fromhex(private_key), "DER")
    pub_key = rsa.PublicKey(priv_key.n, priv_key.e)
    return pub_key.save_pkcs1("DER").hex()


def is_valid_input_structure(input: TransactionInput):
    if input is None:
        return False
    elif not isinstance(input.signature, str):
        return False
    elif not isinstance(input.output_id, str):
        return False
    elif not isinstance(input.output_index, int):
        return False

    return True


def is_valid_output_structure(output: TransactionOutput):
    if output is None:
        return False
    elif not isinstance(output.address, str):
        return False
    elif not isinstance(output.amount, int):
        return False

    return True


def is_valid_transactions_structure(transactions: List[Transaction]):
    for transaction in transactions:
        if not is_valid_transaction_structure(transaction):
            return False
    return True


def is_valid_transaction_structure(transaction: Transaction):
    if not isinstance(transaction.id, str):
        return False

    if not isinstance(transaction.inputs, List):
        return False

    for input in transaction.inputs:
        if not is_valid_input_structure(input):
            return False

    if not isinstance(transaction.outputs, List):
        return False

    for output in transaction.outputs:
        if not is_valid_output_structure(output):
            return False

    return True
