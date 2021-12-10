import sys
from server import server

if __name__ == '__main__':
    try:
        port = sys.argv[1]
    except:
        port = 5000

    server.run(port)
