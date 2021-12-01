import socket

from utils import *


# def sync_protocol(path, server_ip, server_port, recognizer):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((server_ip, int(server_port)))
#     event_handler = MonitorFolder(socket, recognizer)
#     observer = Observer()
#     observer.schedule(event_handler, path, recursive=True)
#     observer.start()


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
    send_all(s, source_folder_path, os.getcwd())
    return recognizer


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


def main(server_ip, server_port, dir_folder, recognizer, time, client_index):
    """
    main function
    :param server_ip: is the sever ip.
    :param server_port:  is the server port.
    :param dir_folder: is the directed folder.
    :param recognizer: is the client recognizer.
    :param time: is the amount of time that the client should be in sleep mode.
    :param client_index: is the client index in the clients_dic dictionary.
    :return:
    """
    # recognized and connected to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, int(server_port)))
    s.send(recognizer.encode(FORMAT))
    s.recv(25)
    s.send(client_index.encode(FORMAT))

    # checking if the recognizer is exists.
    if recognizer == CLIENT_NOT_RECOGNIZED:
        recognizer = no_recognized_protocol(s, recognizer, dir_folder, client_index)

    else:
        # checking the case that the recognizer is exists and the index does not
        if client_index == CLIENT_HAS_NO_INDEX:
            client_index = s.recv(SIZE).decode(FORMAT)
            s.send(b'index received')
            recognized_protocol(s, recognizer, dir_folder)
        # Check the case where the recognizer and index exist
        else:
            pass
            # check for changes
    s.close()


if __name__ == "__main__":
    # if len(sys.argv) < 5 or len(sys.argv) > 6:
    #     exit()
    # elif len(sys.argv) == 6:
    #     RECOGNIZE = sys.argv[5]
    RECOGNIZE = CLIENT_NOT_RECOGNIZED
    # RECOGNIZE = "1asvRx81Xs6UGDfUO2GgN8hsXtjbASyq78ubHps3BBNUzFhNumVVFDbUv5lwSr3SCdcli1DOdCKtbIXGHnrLIAbmJNInBoCyu4ZN5JtMIcGn2ktwCrEfJXF9wcgIYuRZ"
    SERVER_IP = "127.0.0.1"  # sys.argv[1]
    SERVER_PORT = "12347"  # sys.argv[2]
    DIR_FOLDER = "/home/shoval/PycharmProjects/sagiandshoval"  # sys.argv[3]
    # DIR_FOLDER = "/home/sagi/PycharmProjects/IntroNetEx2-Client2"  # sys.argv[3]
    TIME = "5"  # sys.argv[4]
    CLIENT_INDEX = CLIENT_HAS_NO_INDEX
    main(SERVER_IP, SERVER_PORT, DIR_FOLDER, RECOGNIZE, TIME, CLIENT_INDEX)
