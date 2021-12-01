import socket

from utils import *

SERVER_PORT = "12347"  # sys.argv[1]
RECOGNIZER_SIZE = 128

# create the TCP socket and bind with the receiving port.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', int(SERVER_PORT)))
server_socket.listen(5)

# Save the server path location.
server_folder = os.getcwd()

i = 0
# This loop will cause the server to listen and loop for clients.
while True:
    # Accept a new client and read his recognizer string.
    client_socket, client_address = server_socket.accept()
    client_socket.recv(SIZE)
    client_socket.send(b'ok')
    receive_changes(client_socket)
    client_socket.close()
