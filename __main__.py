import sys
from model import wallet
from model.blockchain import Blockchain
from server import server
from network import p2p_server
from threading import Thread

if __name__ == '__main__':
    http_port = None
    p2p_port = None
    try:
        http_port = int(sys.argv[1])
        p2p_port = int(sys.argv[2])
    except:
        if http_port is None:
            http_port = 5000
        if p2p_port is None:
            p2p_port = 6000

    wallet.init_wallet()
    blockchain = Blockchain()
    thread = Thread(target=p2p_server.init, args=[p2p_port, blockchain])
    thread.daemon = True
    thread.start()
    server.run(http_port, blockchain)
