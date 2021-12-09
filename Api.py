import json
from flask import Flask, jsonify
from blockchain import Blockchain
from utils.block_json_encoder import BlockJSONEncoder

app = Flask(__name__)
app.json_encoder = BlockJSONEncoder

blockchain = Blockchain()


@app.route('/', methods=['GET'])
def main():
    wl = '''
    <html>
    <head>Blockchain iteractive API Test</head>
    <body>
       <br></br>
       <a href='mineblock'>mine</a>
       <br></br>
       <a href='chain'>go to chain</a>
    </body> 
     '''
    return wl


@app.route('/mineblock', methods=['GET'])
def mineblock():

    # minerar novo block
    prev_block = blockchain.previous_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)

    generated_block = blockchain.create_block(
        previous_hash=prev_hash, proof=proof)

    # retornar uma resposta para o cliente (navegador ou Postman)
    response = {'message': "Block_mined:",
                'index': generated_block['index'],
                'timestamp': generated_block['timestamp'],
                'proof': generated_block['proof'],
                'previous block': generated_block['previous_hash']}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def getchain():
    response = {'chain': blockchain.chain,
                'len': len(blockchain.chain)}

    return jsonify(response), 200


# inicializa a api
app.run(host='0.0.0.0', port=5000)
