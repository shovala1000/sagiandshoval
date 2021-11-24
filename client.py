import os
import socket
import sys
from time import sleep
from utils import *


def recognized_protocol(s, recognizer, dir_folder):
    receive_all(s, dir_folder)


def sync_protocol(path, server_ip, server_port, recognizer):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, int(server_port)))
    event_handler = MonitorFolder(socket, recognizer)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()


def main(server_ip, server_port, dir_folder, recognizer, time):
    # recognized and connected to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, int(server_port)))
    s.send(recognizer.encode(FORMAT))
    if recognizer == CLIENT_NOT_RECOGNIZED:
        recognizer = no_recognied_protocol(s, recognizer, dir_folder)
    else:
        recognized_protocol(s, recognizer, dir_folder)
    s.close()
    # i=0
    # while True:
    #     print(str(i))
    #     i = i+1
    #     sleep(int(time))
    #     sync_protocol(dir_folder,server_ip,server_port,recognizer)


def no_recognied_protocol(s, recognizer, source_folder_path):
    recognizer = s.recv(SIZE).decode(FORMAT)
    s.send(b'recognizer received')
    send_all(s, source_folder_path, os.getcwd())
    return recognizer


if __name__ == "__main__":
    RECOGNIZE = "rhD5EtKGBkMmCewufNLnttdlwJlsgWRsw3zJbcqKxBzfnH1hy3SDIb5HRIYTCw25RNXVtJwD2BiKsOuAbRqwoRbdCqpQZrKltrLudDuAdUlhQMZWh6mFgGzRAnJw6LMI"
    # if len(sys.argv) < 5 or len(sys.argv) > 6:
    #     exit()
    # elif len(sys.argv) == 6:
    #     RECOGNIZE = sys.argv[5]
    # RECOGNIZE = CLIENT_NOT_RECOGNIZED
    SERVER_IP = "127.0.0.1"  # sys.argv[1]
    SERVER_PORT = "12346"  # sys.argv[2]
    DIR_FOLDER = "/home/shoval/PycharmProjects/sagiandshoval"  # sys.argv[3]
    TIME = "5"  # sys.argv[4]
    main(SERVER_IP, SERVER_PORT, DIR_FOLDER, RECOGNIZE, TIME)
