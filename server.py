import os.path
import socket
import sys

from utils import *


def insert_changes_to_other_clients(clients_dic, client_recognizer, client_index, save_event_queue):
    """
    insert changes to other clients.
    :param clients_dic: is a dic of all clients key: their recognazer, value: dic: key: client's
            index value: client's changes_queue
    :param client_recognizer: is the client recognizer
    :param client_index: is the client index
    :param save_event_queue: is the queue we want to insert
    :return: the client_dic after inserting.
    """
    # temporary_queue
    temp_queue = EventQueue()
    # loop that runs on all clients with the same recognizer
    for index in clients_dic[client_recognizer]:
        # insert the queue of changes to all clients except for the client with the client_recognizer
        if not int(index) == int(client_index):
            while not save_event_queue.empty():
                event = save_event_queue.get()
                temp_queue.put(event)
                clients_dic[client_recognizer][int(index)].put(event)
        while not temp_queue.empty():
            save_event_queue.put(temp_queue.get())
    return clients_dic


def add_index_to_dict(s, clients_dic, client_recognizer):
    """
    The function receives  a client recognizer and the dictionary.
    The function will create another index the the dictionary on the client recognizer key.
    Client could use more than one computer but he has only one recognizer, so this dictionary helps us to find
    the right computer.
    :param s: is the socket
    :param clients_dic: is the dictionary
    :param client_recognizer: is the client recognizer.
    :return:
    """
    # find the number of clients that already exists with the same recognizer.
    number_of_key = len(clients_dic[client_recognizer].keys())
    # create new client index, inset to the dict with new queue.
    client_index = number_of_key + 1
    clients_dic[client_recognizer][client_index] = EventQueue()
    # send the index to the client.
    s.send(str(client_index).encode(FORMAT))
    return client_index


def no_recognized_protocol(s, recognizer_size, clients_dic, clients_address_dic):
    """
    The function will be called when the client recognizer does not exits.
    The method we use is that the server generate a new recognizer for the client and when the client receive the
    recognizer from the server he sends all the data to the server.
    :param s: is the socket
    :param recognizer_size: is the client recognizer size.
    :param clients_dic: this dictionary contain client recognizes as keys and each of them has dictionary that
     contains the clients indexes and their event queue as value.
    :param clients_address_dic: this dictionary contain client recognizes as keys and their tacking path as value.
    :return: nothing.
    """
    # make random recognizer for client
    client_recognizer = get_random_string(recognizer_size)
    # sending the client recognizer.
    s.send(client_recognizer.encode(FORMAT))
    s.recv(SIZE).decode(FORMAT)
    # create a folder in the  server folder path with the name of the recognizer.
    os.makedirs(client_recognizer)
    tracking_path = os.path.join(os.getcwd(), client_recognizer)
    clients_address_dic[client_recognizer] = tracking_path
    # save in client_dict
    clients_dic[client_recognizer] = {}
    # adding new index to the dict and receive the data.
    add_index_to_dict(s, clients_dic, client_recognizer)
    receive_all(s, tracking_path)


def recognized_protocol(s, recognizer, clients_address_dic):
    """
    The function handles the case that the recognize exists and the index does not exists.
    In this case the the server should send all the files in the directed folder to the client.
    We chose to use a dictionary that hold the client recognizer as key and the tracking path as a value.
    The program needs to handle a case that several clients has the same recognizer but all of them should track on
    the same folder. This dictionary helps us to know what is the tracking path for each client.
    :param s: is the socket
    :param recognizer: is the client recognizer.
    :param clients_address_dic: is the address for the folder.
    """

    # sending all the folders and files.
    path = clients_address_dic.get(recognizer)
    send_all(s, path)


def main(server_port, recognizer_size):
    """
    main function.
    :param server_port:  is the server port.
    :param recognizer_size: is the length of the client recognizer string.
    """
    # create the TCP socket and bind with the receiving port.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(server_port)))
    server_socket.listen(5)

    # create a list for saving the clients recognizers and the folder that related to each client.
    clients_dic = {}
    clients_address_dic = {}

    # This loop will cause the server to listen and loop for clients.
    while True:
        # Accept a new client and read his recognizer string.
        client_socket, client_address = server_socket.accept()
        client_recognizer = client_socket.recv(recognizer_size).decode(FORMAT)
        client_socket.send(b'recognizer received')
        client_index = client_socket.recv(recognizer_size).decode(FORMAT)

        if client_recognizer == CLIENT_NOT_RECOGNIZED:
            no_recognized_protocol(client_socket, recognizer_size, clients_dic, clients_address_dic)
        else:
            if client_index == CLIENT_HAS_NO_INDEX:
                client_index = add_index_to_dict(client_socket, clients_dic, client_recognizer)
                client_socket.recv(SIZE).decode(FORMAT)
                recognized_protocol(client_socket, client_recognizer, clients_address_dic)
            else:
                client_socket.send(b'start sync')
                # receive client's changes.
                save_events_queue = receive_changes(client_socket, clients_address_dic[client_recognizer])
                clients_dic = insert_changes_to_other_clients(clients_dic, client_recognizer, client_index,
                                                              save_events_queue)

                client_socket.recv(SIZE).decode(FORMAT)
                path_without_main_dir = clients_address_dic[client_recognizer]
                # send changes to client
                send_changes(clients_dic[client_recognizer][int(client_index)], client_socket, path_without_main_dir)
        client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit()
    SERVER_PORT = sys.argv[1]
    RECOGNIZER_SIZE = 128
    main(SERVER_PORT, RECOGNIZER_SIZE)
