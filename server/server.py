from threading import Thread
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from model import Blockchain
from utils import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mineblock():
    args = request.args

    if args is not None and args.get("stop") is not None:
        blockchain.stop_mining()
    else:
        thread = Thread(target=blockchain.mine)
        thread.daemon = True
        thread.start()

    response = {
        'mining': blockchain.mining
    }

    return jsonify(response), 200


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
    coins = 0
    print("Counting coins")
    for node in blockchain.chain :
        for tr in node.__dict__['transactions'] : 
            coins = coins + int(tr.__dict__['amount'])

    return render_template('chain.html', value=str(coins), message=response), 200
    # return jsonify(response,), 200


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
