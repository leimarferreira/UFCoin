import sys
from model import wallet
from model.blockchain import Blockchain
from server import server
from network import p2p_server
from threading import Thread

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except:
        port = 5000

    wallet.init_wallet()
    blockchain = Blockchain()
    thread = Thread(target=p2p_server.init, args=[blockchain])
    thread.daemon = True
    thread.start()
    server.run(port, blockchain)
