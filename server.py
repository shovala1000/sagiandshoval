import os
import socket
import sys
from utils import *


def add_index_to_dict(s, clients_dic, client_recognizer):
    """
    The function
    :param s:
    :param clients_dic:
    :param client_recognizer:
    :return:
    """
    # find the number of clients that already exists with the same recognizer.
    number_of_key = len(clients_dic[client_recognizer].keys())
    # create new client index, inset to the dict with new queue.
    client_index = number_of_key + 1
    clients_dic[client_recognizer][client_index] = EventQueue()
    # send the index to the client.
    s.send(str(client_index).encode(FORMAT))


def no_recognized_protocol(s, recognizer, recognizer_size, clients_dic):
    # make random recognizer for client
    client_recognizer = get_random_string(recognizer_size)
    # sending the client recognizer.
    s.send(client_recognizer.encode(FORMAT))
    s.recv(SIZE).decode(FORMAT)
    # create a folder in the  server folder path with the name of the recognizer.
    os.makedirs(client_recognizer)
    tracking_path = os.path.join(os.getcwd(), client_recognizer)
    # save in client_dict
    clients_dic[client_recognizer] = {}
    add_index_to_dict(s, clients_dic, client_recognizer)
    receive_all(s, tracking_path)


def recognized_protocol(socket, recognizer, client_dic):
    path = client_dic.get(recognizer)
    main_dir = os.listdir(path)[0]
    in_path = os.path.join(path, main_dir)
    send_all(socket, in_path, path)


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
        client_socket.send(b'recognizer received')
        client_index = client_socket.recv(SIZE)
        if client_recognizer == CLIENT_NOT_RECOGNIZED:
            no_recognized_protocol(client_socket, client_recognizer, recognizer_size, clients_dic)
        else:
            if client_index == CLIENT_HAS_NO_INDEX:
                add_index_to_dict(client_socket, clients_dic, client_recognizer)
                recognized_protocol(client_socket, client_recognizer, clients_dic)
            else:
                pass
                # Check for changes.

        client_socket.close()


if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     exit()
    SERVER_PORT = "12346"  # sys.argv[1]
    RECOGNIZER_SIZE = 128
    main(SERVER_PORT, RECOGNIZER_SIZE)
