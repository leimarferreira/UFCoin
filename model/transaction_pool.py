from copy import deepcopy
from typing import List

from transaction import (Transaction, TransactionInput,
                         UnspentTransactionOutput, validate_transaction)

transaction_pool: List[Transaction] = []


def get_transaction_pool():
    return deepcopy(transaction_pool)


def add_to_transaction_pool(transaction: Transaction, unspent_outputs: List[UnspentTransactionOutput]):
    if not validate_transaction(transaction, unspent_outputs):
        raise RuntimeError(
            "Trying to add invalid transaction to transaction pool.")

    if not is_valid_transaction_for_pool(transaction, transaction_pool):
        raise RuntimeError(
            "Trying to add invalid transaction to transaction pool.")

    transaction_pool.append(transaction)


def has_input(input: TransactionInput, unspent_outputs: List[UnspentTransactionOutput]):
    for transaction in unspent_outputs:
        if transaction.output_id == input.output_id and transaction.output_index == input.output_index:
            return True

    return False


def update_transaction_pool(unspent_outputs: List[UnspentTransactionOutput]):
    invalid_transactions = []

    for transaction in transaction_pool:
        for input in transaction.inputs:
            if not has_input(input, unspent_outputs):
                invalid_transactions.append(input)
                break

    if len(invalid_transactions) > 0:
        transaction_pool = list(
            set(transaction_pool) - set(invalid_transactions))


def get_pool_inputs(transaction_pool: List[Transaction]):
    inputs = []
    for transaction in transaction_pool:
        inputs.extend(transaction.inputs)

    return inputs


def is_valid_transaction_for_pool(transaction: Transaction, pool: List[Transaction]):
    pool_inputs: List[TransactionInput] = get_pool_inputs(transaction_pool)

    for input in transaction.inputs:
        for pool_input in pool_inputs:
            if input.output_id == pool_input.output_id and input.output_index == pool_input.output_index:
                return False

    return True
