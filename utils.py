
import os
import string
import random
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket

FORMAT = 'utf-8'
SIZE = 1024
CLIENT_NOT_RECOGNIZED = 'no recognize'
BYTES_FOR_INDEX = 4
END_DIRS = 'End dirs'
END_FILES = 'End files'
END_ONE_FILE = b'End one file'
END_SEND_ALL = b'end_send_all'


class MonitorFolder(FileSystemEventHandler):
    s = socket
    r = ''

    def __init__(self, s,recognizer):
        self.s = s
        self.r = recognizer

    def on_created(self, event):
        pass
        # def on_modified(self, event):

    def on_deleted(self, event):
        self.s.settimeout(5)
        try:
            self.s.send("on_deleted".encode(FORMAT))
            self.s.recv(SIZE)
            self.s.send((self.r).encode(FORMAT))
            self.s.recv(SIZE)
        except:
            pass
        event = os.path.relpath(event.src_path)
        socket.send(event.encode(FORMAT))

        print("on_deleted " + event)

    def on_moved(self, event):
        print("on_moved")

    # def on_any_event(self, event):
    #     print("on_any_event")


def get_random_string(length):
    """
    :param length: is the string length.
    :return: The function creates a string that contain digits or english lower and upper case letters.
    """
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for i in range(length))


def send_file_data(socket, file_name, path,start):
    # send to server the file name
    socket.send(os.path.join(os.path.relpath(path,start),file_name).encode(FORMAT))
    socket.recv(SIZE).decode(FORMAT)
    # open the file and read data
    new_file = open(os.path.join(path, file_name), 'rb')
    data = new_file.read(SIZE)
    while data:
        socket.send(data)
        socket.recv(SIZE)
        data = new_file.read(SIZE)
    # receive for the client will know we finish sending the file data
    socket.send(END_ONE_FILE)
    socket.recv(SIZE).decode(FORMAT)
    new_file.close()


def send_dir_inf(socket, source_folder_path,start):
    # start_with_folder = os.path.basename(source_folder_path)
    for dir_path, dirs_list, files_list in os.walk(source_folder_path, topdown=True):
        # send the dir_path.
        socket.send(dir_path.encode(FORMAT))
        socket.recv(SIZE)
        # sending all the dirs names
        for dir_name in dirs_list:
            socket.send(os.path.join(os.path.relpath(dir_path,start),dir_name).encode(FORMAT))
            socket.recv(SIZE).decode(FORMAT)
        # finished with sending the dirs and starting with sending the files
        socket.send(END_DIRS.encode(FORMAT))
        socket.recv(SIZE).decode(FORMAT)
        for file_name in files_list:
            send_file_data(socket, file_name, dir_path, start)
        # finished with sending all
        socket.send(END_FILES.encode(FORMAT))
        socket.recv(SIZE)
    socket.send(END_SEND_ALL)


def send_all(socket, source_dir_path,start):
    # send thee name of the file or folder
    folder_normpath = os.path.normpath(source_dir_path)
    folder_name = os.path.basename(folder_normpath)

    # socket.send(folder_name.encode(FORMAT))
    send_dir_inf(socket, source_dir_path,start)


def receive_dirs_from_path(socket, path):
    dir_name = bytes(socket.recv(SIZE)).decode(FORMAT)
    socket.send(b'dir_name received')

    while not dir_name == END_DIRS:
        dir_path = os.path.join(path, dir_name)
        os.makedirs(dir_path)
        dir_name = bytes(socket.recv(SIZE)).decode(FORMAT)

        socket.send(b'dir_name received')


def receive_files_from_path(socket, path):
    file_name = bytes(socket.recv(SIZE)).decode(FORMAT)
    socket.send(b'file_name received')
    while not file_name == END_FILES:
        # creates the file
        file_path = os.path.join(path, file_name)
        with open(file_path, 'wb') as f:
            file_data = socket.recv(SIZE)

            socket.send(b'file_data received')
            while not file_data == END_ONE_FILE:
                f.write(file_data)
                file_data = socket.recv(SIZE)

                socket.send(b'file_data received')
        f.close()
        file_name = bytes(socket.recv(SIZE)).decode(FORMAT)

        socket.send(b'file_name received')


def receive_all(socket, put_in_folder_path):
    # receive the main dir
    dir = bytes(socket.recv(SIZE)).decode(FORMAT)
    socket.send(b' dir received')
    path = os.path.join(put_in_folder_path, os.path.basename(dir))
    os.makedirs(path)

    while not dir == END_SEND_ALL.decode(FORMAT):
        # receive all the folders in dir
        receive_dirs_from_path(socket, put_in_folder_path)

        # receive all the files in dir
        receive_files_from_path(socket, put_in_folder_path)

        dir = bytes(socket.recv(SIZE)).decode(FORMAT)
        socket.send(b' dir received')
        # path = os.path.join(put_in_folder_path, os.path.basename(dir))
