import os.path
import socket
import time
from queue import Empty

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
    # sending the main_dir name
    # s.recv(SIZE)
    # s.send(os.path.basename(dir_folder).encode(FORMAT))
    receive_all(s, dir_folder)


def init_socket(server_ip, server_port, recognizer, client_index):
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
    :return:
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
        # Check the case where the recognizer and index exist

    # initialize handler and observer
    my_event_queue = EventQueue()
    my_handler = MonitorFolder(RECOGNIZE, my_event_queue)
    my_observer = Observer()
    my_observer.schedule(my_handler, dir_folder, True)
    my_observer.start()
    # check for changes
    black_events_queue = EventQueue()
    while True:
        s.close()
        time.sleep(int(time_waiting))
        s = init_socket(server_ip, server_port, recognizer, client_index)
        # received start sync
        s.recv(SIZE)
        save_event_queue = remove_received_changes(my_handler.get_queue(), black_events_queue)
        print('my_handler.get_queue(): '+str(my_handler.get_queue().queue))
        print('black_events_queue: '+str(black_events_queue.queue))
        print('save_event_queue: '+str(save_event_queue.queue))
        send_changes(save_event_queue, s, dir_folder)
        s.send(os.path.basename(dir_folder).encode(FORMAT))
        # receive changes from server.
        black_events_queue = receive_changes(s, dir_folder)
        # print('black_events_queue: ' + str(black_events_queue.queue))


def remove_received_changes(save_queue, black_queue):
    temp_queue = EventQueue()
    while not black_queue.empty():
        # print(str(len(black_queue)))
        black_event = black_queue.get()
        while not save_queue.empty():
            save_event = save_queue.get()
            if not save_event == black_event:
                temp_queue.put(save_event)
        while not temp_queue.empty():
            save_queue.put(temp_queue.get())

    # print('black_queue: ' + str(black_queue.queue))
    # print('save_queue: ' + str(save_queue.queue))
    return save_queue


if __name__ == "__main__":
    # if len(sys.argv) < 5 or len(sys.argv) > 6:
    #     exit()
    # elif len(sys.argv) == 6:
    #     RECOGNIZE = sys.argv[5]
    RECOGNIZE = CLIENT_NOT_RECOGNIZED
    RECOGNIZE = "1BZhbauC9CH9vXsF4EKk1IXM8so0gxFDOSES0EqMWKgSViEJoLQvvULISuXXP2I1MYxBG01jjBXKhVYdXX4JKsANVmizhjWPE5h769ZrKQG17sLk9hOANckfs3dL4Zdp"
    SERVER_IP = "127.0.0.1"  # sys.argv[1]
    SERVER_PORT = "12347"  # sys.argv[2]
    DIR_FOLDER = "/home/shoval/Desktop/client2"  # sys.argv[3]
    # DIR_FOLDER = "/home/sagi/PycharmProjects/IntroNetEx2-Client2"  # sys.argv[3]
    TIME = "7"  # sys.argv[4]
    CLIENT_INDEX = CLIENT_HAS_NO_INDEX
    main(SERVER_IP, SERVER_PORT, DIR_FOLDER, RECOGNIZE, TIME, CLIENT_INDEX)
