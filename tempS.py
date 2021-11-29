from utils import *

SERVER_PORT = "12346"  # sys.argv[1]
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
    dir_path = client_socket.recv(SIZE)
    client_socket.send(b'dir_path_received')
    # client_socket.settimeout(10)
    print("i = " + str(i))
    i = i + 1
    # try:
    print(client_socket.recv(SIZE).decode(FORMAT))
    client_socket.send(b'change received')
    # except:
    #     pass
    client_socket.close()
