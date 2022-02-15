from crypt import methods
import re
import sys
import webbrowser
from ctypes import addressof
from threading import Thread
from uuid import uuid4

from flask import Flask, redirect, render_template, request, url_for
from model.blockchain import Blockchain
from model.wallet import get_identifier, init_wallet
from utils import CustomJSONEncoder
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

blockchain: Blockchain = None


@app.route('/')
def index():
    response = {
        'title': "Início",
        'address': ip_address,
        'http_port': _http_port,
        'p2p_port': p2p_port
    }

    return render_template('index.html', **response), 200


@app.route('/wallet')
def wallet():
    response = {
        'title': 'Carteira',
        'coins': blockchain.get_account_balance(),
        'address': get_identifier()
    }

    return render_template('wallet.html', **response), 200


@app.route('/transaction/new/')
def add():
    response = {
        'title': "Transações"
    }

    return render_template('transaction.html', **response), 200


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
        'title': 'Minerar',
        'mining': blockchain.mining
    }
    return render_template('mine.html', **response), 200


@app.route("/transaction/new/add", methods=["POST"])
def new_transaction():
    if request.method == 'POST':
        receiver = request.form['receiver']
        amount = request.form['amount']

        if not (receiver or amount):
            return 'Missing values', 400

        blockchain.send_transaction(receiver, int(amount))

        message = "A transação vai ser adicionada ao próximo bloco minerado."
        return render_template('transaction.html', message=message), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'title': 'Blockchain',
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return render_template('chain.html', **response), 200


@app.route("/nodes/register", methods=["GET", "POST"])
def register_node():
    if request.method == 'POST':
        address = request.form['address']
        if re.match('^ws://([0-9]{1,3}\\.){3}[0-9]{1,3}:[0-9]{1,5}$', address):
            blockchain.register_node(address)

    response = {
        'peers': blockchain.get_nodes()
    }

    return render_template('peers.html', **response)


@app.route("/login", methods=["GET", "POST"])
def login():
    global user_identified

    if user_identified:
        redirect("/")

    if request.method == 'POST':
        user = request.form['username']
        passwd = request.form['password']
        init_wallet(user, passwd)
        user_identified = True
        return redirect(url_for('index'))

    response = {
        'title': "Login"
    }

    return render_template("login.html", **response)


@app.before_request
def before_all():
    global user_identified
    path = request.path

    if re.match('^/static/.*', path):
        return

    if user_identified and path == "/login":
        return redirect(url_for("index"))
    elif not user_identified and path != "/login":
        return redirect(url_for("login"))


@app.errorhandler(HTTPException)
def error(e):
    response = {
        'title': "Erro",
        'message': "Ocorreu um erro durante realização da operação."
    }
    return render_template("error.html", **response)


@app.errorhandler(404)
def not_found(e):
    response = {
        'title': "Página não encontrada",
        'message': "Página não encontrada."
    }
    return render_template("error.html", **response)


def run(ip_addr, http_port, ws_port, chain):
    global p2p_port
    global _http_port
    global blockchain
    global ip_address
    global user_identified
    user_identified = False
    ip_address = ip_addr
    _http_port = http_port
    p2p_port = ws_port
    blockchain = chain

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(ip_addr, http_port)
