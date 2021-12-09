import os.path
import socket
import sys
import time
import watchdog.events
from watchdog.observers import Observer
from utils import *


def no_recognized_protocol(s, recognizer, source_folder_path, client_index):
    """
    The function will be called when the client recognizer does not exits.
    The method we use is that the server generate a new recognizer for the client and when the client receive the
    recognizer from the server he sends all the data to the server.
    :param s: is the socket.
    :param recognizer: is the client recognizer.
    :param source_folder_path: is the source folder path
    :param client_index: is the client index in the clients dict,
     for case that there are several clients on the same recognizer.
    :return: the client recognizer.
    """
    recognizer = s.recv(SIZE).decode(FORMAT)
    s.send(b'recognizer received')
    client_index = s.recv(SIZE).decode(FORMAT)
    send_all(s, source_folder_path)
    return recognizer, client_index


def recognized_protocol(s, recognizer, dir_folder):
    """
    The function handles the case that the recognize exists and the index does not exists.
    In this case the the server should send all the files in the directed folder to the client.
    :param s: is the socket
    :param recognizer: is the client recognizer.
    :param dir_folder: is the directed folder.
    :return: nothing.
    """

    receive_all(s, dir_folder)


def init_socket(server_ip, server_port, recognizer, client_index):
    """
    initialize sockent and connection with the server
    :param server_ip: is the server's ip
    :param server_port: is the server's port
    :param recognizer: is the client recognizer
    :param client_index: is the client's index
    :return:
    """
    # recognized and connected to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, int(server_port)))
    s.send(recognizer.encode(FORMAT))
    s.recv(25)
    s.send(client_index.encode(FORMAT))
    return s


def main(server_ip, server_port, dir_folder, recognizer, time_waiting, client_index):
    """
    main function
    :param time_waiting:
    :param server_ip: is the sever ip.
    :param server_port:  is the server port.
    :param dir_folder: is the directed folder.
    :param recognizer: is the client recognizer.
    :param client_index: is the client index in the clients_dic dictionary.
    """
    # initalize socket
    s = init_socket(server_ip, server_port, recognizer, client_index)
    # checking if the recognizer is exists.
    if recognizer == CLIENT_NOT_RECOGNIZED:
        recognizer, client_index = no_recognized_protocol(s, recognizer, dir_folder, client_index)

    else:
        # checking the case that the recognizer is exists and the index does not
        if client_index == CLIENT_HAS_NO_INDEX:
            client_index = s.recv(SIZE).decode(FORMAT)
            s.send(b'index received')
            recognized_protocol(s, recognizer, dir_folder)

    # initialize handler and observer
    my_event_queue = EventQueue()
    my_handler = MonitorFolder(RECOGNIZE, my_event_queue)
    my_observer = Observer()
    my_observer.schedule(my_handler, dir_folder, True)
    my_observer.start()
    # black queue for the events the client received.
    black_events_queue = EventQueue()
    # loop that runs forever for sync with the server (sending and receiving changes)
    while True:
        s.close()
        time.sleep(int(time_waiting))
        s = init_socket(server_ip, server_port, recognizer, client_index)
        # received start sync
        s.recv(SIZE)
        # save_event_queue is a queue with all the changes the client did
        save_event_queue = my_handler.get_queue()

        temp_queue = EventQueue()
        while not save_event_queue.empty():
            current_event = save_event_queue.get()
            if current_event.event_type == watchdog.events.EVENT_TYPE_CLOSED:
                temp2_queue = EventQueue()
                while not temp_queue.empty():
                    temp_event = temp_queue.get()
                    if temp_event.event_type == watchdog.events.EVENT_TYPE_CREATED or temp_event.event_type == watchdog.events.EVENT_TYPE_DELETED:
                        if not temp_event.src_path == current_event.src_path:
                            temp2_queue.put(temp_event)
                    else:
                        temp2_queue.put(temp_event)
                while not temp2_queue.empty():
                    temp_queue.put(temp2_queue.get())

            else:
                temp_queue.put(current_event)
        while not temp_queue.empty():
            save_event_queue.put(temp_queue.get())
        # removing all the changes the client just received
        remove_received_changes(my_handler.get_queue(), black_events_queue)
        # send all changes to the server
        send_changes(save_event_queue, s, dir_folder)
        s.send(os.path.basename(dir_folder).encode(FORMAT))
        # save the events the client received.
        black_events_queue = receive_changes(s, dir_folder)


def remove_received_changes(save_queue, black_queue):
    """
    removing all the eventsthat in the black_queue from the save_queue
    :param save_queue: is a queue of events
    :param black_queue: is a queue of events
    :return:
    """

    temp_queue = EventQueue()
    while not black_queue.empty():
        black_event = black_queue.get()
        while not save_queue.empty():
            save_event = save_queue.get()
            if not save_event == black_event:
                temp_queue.put(save_event)
        while not temp_queue.empty():
            save_queue.put(temp_queue.get())

    return save_queue


if __name__ == "__main__":
    RECOGNIZE = CLIENT_NOT_RECOGNIZED
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        exit()
    elif len(sys.argv) == 6:
        RECOGNIZE = sys.argv[5]
    SERVER_IP = sys.argv[1]
    SERVER_PORT = sys.argv[2]
    DIR_FOLDER = sys.argv[3]
    TIME = sys.argv[4]
    CLIENT_INDEX = CLIENT_HAS_NO_INDEX
    main(SERVER_IP, SERVER_PORT, DIR_FOLDER, RECOGNIZE, TIME, CLIENT_INDEX)
