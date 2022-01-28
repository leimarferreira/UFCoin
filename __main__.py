import sys
from model import wallet
from server import server

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except:
        port = 5000

    wallet.init_wallet()
    server.run(port)
