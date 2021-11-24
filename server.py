import os
import socket
import sys
from utils import *


def no_recognied_protocol(s, recognizer, recognizer_size, clients_dic):
    # make random recognizer for client
    client_recognizer = get_random_string(recognizer_size)

    # sending the client recognizer.
    s.send(client_recognizer.encode(FORMAT))
    s.recv(SIZE)
    # create a folder in the  server folder path with the name of the recognizer.
    os.makedirs(client_recognizer)
    tracking_path = os.path.join(os.getcwd(), client_recognizer)
    # save in client_dic
    clients_dic[client_recognizer] = tracking_path
    receive_all(s, tracking_path)


def recognized_protocol(socket, recognizer, client_dic):
    path = client_dic.get(recognizer)
    main_dir = os.listdir(path)[0]
    in_path = os.path.join(path, main_dir)
    send_all(socket, in_path,path)


def main(server_port, recognizer_size):
    """
    :param server_port:  is the server port.
    :param recognizer_size: is the length of the client recognizer string.
    :return: Main function for server.
    """

    # create the TCP socket and bind with the receiving port.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', int(server_port)))
    server_socket.listen(5)

    # create a list for saving the clients recognizers and the folder that related to each client.
    clients_dic = {}

    # Save the server path location.
    server_folder = os.getcwd()

    # This loop will cause the server to listen and loop for clients.
    while True:
        # Accept a new client and read his recognizer string.
        client_socket, client_address = server_socket.accept()
        client_recognizer = client_socket.recv(recognizer_size).decode(FORMAT)
        if client_recognizer == CLIENT_NOT_RECOGNIZED:
            no_recognied_protocol(client_socket, client_recognizer, recognizer_size, clients_dic)
        else:
            if client_recognizer == "on_deleted":
                client_recognizer = client_socket.recv(recognizer_size).decode(FORMAT)
                client_socket.send(b'client_recognizer received')
                dir_to_delete = client_socket.recv(SIZE)
                client_socket.send(b'on_deleted received')
                os.remove(os.path.join(clients_dic[client_recognizer], dir_to_delete))
            else:
                recognized_protocol(client_socket, client_recognizer, clients_dic)

        client_socket.close()


if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     exit()
    SERVER_PORT = "12346"  # sys.argv[1]
    RECOGNIZER_SIZE = 128
    main(SERVER_PORT, RECOGNIZER_SIZE)
