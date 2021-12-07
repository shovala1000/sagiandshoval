# import socket
# import time
# from watchdog.observers import Observer
# from watchdog.observers.api import EventQueue
# from utils import *
#
#
# RECOGNIZE = CLIENT_NOT_RECOGNIZED
# SERVER_IP = "127.0.0.1"
# SERVER_PORT = "12345"
# DIR_FOLDER = "/test2"  # sys.argv[3]
# TIME = "20"
#
#
# def init_socket():
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.connect((SERVER_IP, int(SERVER_PORT)))
#     return s
#
#
# s = init_socket()
# my_event_queue = EventQueue()
# my_handler = MonitorFolder(RECOGNIZE, my_event_queue)
# my_observer = Observer()
# my_observer.schedule(my_handler, dir_folder, True)
# my_observer.start()
#
# try:
#     while True:
#         time.sleep(int(TIME))
#         send_changes(my_handler.get_queue(), s)
#         s = init_socket()
# except KeyboardInterrupt:
#     my_observer.stop()
# my_observer.join()

import os

src_path = "/home/shoval/Desktop/test/dir1/city"
source_path = "/home/shoval/Desktop"
print("1. " + os.path.relpath(src_path, source_path))
