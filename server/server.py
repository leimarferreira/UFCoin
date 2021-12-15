from uuid import uuid4

from flask import Flask, jsonify, request
from model import Blockchain
from utils import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mineblock():

    # minerar novo bloco
    last_block = blockchain.last_block
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    blockchain.create_transaction(
        sender='0',
        receiver=node_identifier,
        amount=5
    )

    generated_block = blockchain.create_block(proof=proof)

    # retornar uma resposta para o cliente (navegador ou Postman)
    response = {
        'message': "Block mined",
        'index': generated_block.index,
        'timestamp': generated_block.timestamp,
        'proof': generated_block.proof,
        'previous block': generated_block.previous_hash
    }

    return jsonify(response), 201


@app.route("/transaction/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.create_transaction(
        values['sender'], values['receiver'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response,), 200


@app.route("/nodes/register", methods=["POST"])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }

    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            "message": "Our blockchain has been replaced.",
            "new_chain": blockchain.chain
        }

    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


def run(port):
    app.run('localhost', port)
