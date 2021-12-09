import os.path
import socket
import time
from queue import Empty

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

    # print('RECOGNIZE: '+recognizer)
    while True:
        s.close()
        time.sleep(int(time_waiting))
        s = init_socket(server_ip, server_port, recognizer, client_index)
        # received start sync
        s.recv(SIZE)
        save_event_queue = my_handler.get_queue()
        temp_queue = EventQueue()
        while not save_event_queue.empty():
            current_event = save_event_queue.get()
            print("current_event: "+str(current_event))
            if current_event.event_type == watchdog.events.EVENT_TYPE_CLOSED:
                print("yes1")
                temp2_queue = EventQueue()
                print("temp2: "+str(temp2_queue.queue))
                print("before temp_queue: " + str(temp_queue.queue))
                while not temp_queue.empty():
                    temp_event = temp_queue.get()
                    print("temp_queue: "+str(temp_queue.queue))
                    if temp_event.event_type == watchdog.events.EVENT_TYPE_CREATED or temp_event.event_type == watchdog.events.EVENT_TYPE_DELETED:
                        print('temp: '+temp_event.src_path+"\ncurrent: "+current_event.src_path)
                        if not temp_event.src_path == current_event.src_path:
                            temp2_queue.put(temp_event)
                            print("temp_2: "+str(temp2_queue.queue))
                    else:
                        temp2_queue.put(temp_event)
                while not temp2_queue.empty():
                    temp_queue.put(temp2_queue.get())

            else:
                temp_queue.put(current_event)
                print("temp_ queue2: "+str(temp_queue.queue))
        while not temp_queue.empty():
            save_event_queue.put(temp_queue.get())
        print('\nsending this queue: '+str(save_event_queue.queue))
        remove_received_changes(my_handler.get_queue(), black_events_queue)
        send_changes(save_event_queue, s, dir_folder)
        s.send(os.path.basename(dir_folder).encode(FORMAT))
        # receive changes from server.
        black_events_queue = receive_changes(s, dir_folder)


#         # print('black_events_queue: ' + str(black_events_queue.queue))


def remove_received_changes(save_queue, black_queue):
    print('black_queue: ' + str(black_queue.queue))
    print('save_queue: ' + str(save_queue.queue))
    temp_queue = EventQueue()
    while not black_queue.empty():
        black_event = black_queue.get()
        print('black_event: ' + str(black_event))
        while not save_queue.empty():
            save_event = save_queue.get()
            print("save_event: " + str(save_event))
            if not save_event == black_event:  # and os.path.exists(save_event.src_path):
                print("save event is not black event")
                temp_queue.put(save_event)
        while not temp_queue.empty():
            save_queue.put(temp_queue.get())

    print("end save: " + str(save_queue.queue))
    print("end black: " + str(black_queue.queue))
    print("end temp: " + str(temp_queue.queue))
    return save_queue


if __name__ == "__main__":
    # if len(sys.argv) < 5 or len(sys.argv) > 6:
    #     exit()
    # elif len(sys.argv) == 6:
    #     RECOGNIZE = sys.argv[5]
    RECOGNIZE = CLIENT_NOT_RECOGNIZED
    RECOGNIZE = "MhUYunoKfruxxe5B7ogvyABPlIAscZwRdJ5al94Y31fqzCiAnFjvp6yAZctNepzdme5WfCGisdJxtg8iABHkI9qwHLWdQ2l0IybhdwZj7qjneKnDoQxRjYIGJE60pXvR"
    SERVER_IP = "127.0.0.1"  # "192.168.43.12"  # sys.argv[1]
    SERVER_PORT = "12347"  # sys.argv[2]
    DIR_FOLDER = "/home/shoval/Desktop/client2"  # sys.argv[3]
    # DIR_FOLDER = "/home/sagi/PycharmProjects/IntroNetEx2-Client2"  # sys.argv[3]
    TIME = "7"  # sys.argv[4]
    CLIENT_INDEX = CLIENT_HAS_NO_INDEX
    main(SERVER_IP, SERVER_PORT, DIR_FOLDER, RECOGNIZE, TIME, CLIENT_INDEX)
