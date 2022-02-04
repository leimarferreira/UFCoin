import sys
from threading import Thread
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from model.blockchain import Blockchain
from model.wallet import get_public_key
from utils import CustomJSONEncoder

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

node_identifier = str(uuid4()).replace('-', '')

blockchain: Blockchain = None


@app.route('/')
def index():
    return render_template('index.html'), 200


@app.route('/wallet')
def wallet():
    return render_template('wallet.html'), 200


@app.route('/transaction/new/')
def add():
    return render_template('transaction.html'), 200


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
    return render_template('mine.html', message=response), 200


@app.route("/transaction/new/add", methods=["POST"])
def new_transaction():
    if request.method == 'POST':
        receiver = request.form['receiver']
        amount = request.form['amount']

        if not (receiver or amount):
            return 'Missing values', 400

        blockchain.send_transaction(receiver, int(amount))

        response = {
            'message': f'Transaction will be added to the next mined block.'}
        return render_template('transaction.html', message=response), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    coins = blockchain.get_account_balance()

    return render_template('chain.html', chain=blockchain.chain), 200


@app.route("/nodes/register", methods=["POST"])
def register_node():
    node = request.json['node']
    blockchain.register_node(node)
    return "ok", 201


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


@app.route("/address", methods=["GET"])
def get_address():
    address = get_public_key()

    response = {
        'address': address
    }

    return jsonify(response), 200


@app.route("/balance", methods=["GET"])
def balance():
    balance = blockchain.get_account_balance()

    response = {
        'balance': balance
    }

    return jsonify(response), 200


def run(port, chain):
    global blockchain
    blockchain = chain
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run('localhost', port)
