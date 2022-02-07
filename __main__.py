from concurrent.futures import thread
import socket
import sys
from time import sleep
import webbrowser
from threading import Thread

from model import wallet
from model.blockchain import Blockchain
from network import p2p_server
from server import server


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('254.254.254.254', 1))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'


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
    ip = get_ip_address()
    blockchain = Blockchain()
    p2p_thread = Thread(target=p2p_server.init, args=[ip, p2p_port, blockchain])
    p2p_thread.daemon = True
    p2p_thread.start()

    http_thread = Thread(target=server.run, args=[ip, http_port, p2p_port, blockchain])
    http_thread.start()

    sleep(2)

    webbrowser.open(f'http://{ip}:{http_port}')
