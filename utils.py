import os
import string
import random
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers.api import EventEmitter

import socket

FORMAT = 'utf-8'
SIZE = 1024
CLIENT_NOT_RECOGNIZED = 'no recognize'
BYTES_FOR_INDEX = 4
END_DIRS = 'End dirs'
END_FILES = 'End files'
END_ONE_FILE = b'End one file'
END_SEND_ALL = b'end_send_all'


# class MonitorFolder(FileSystemEventHandler):
#     s = socket
#     r = ''
#
#     def __init__(self, s,recognizer):
#         self.s = s
#         self.r = recognizer


def on_created(event):
    """Called when a file or directory is created.
    :param event:
        Event representing file/directory creation.
    """
    print(f"on_created: {event.src_path}")


def on_deleted(event):
    """Called when a file or directory is deleted.
     :param event:
         Event representing file/directory deletion.
     """
    print(f"on_deleted: {event.src_path}")


def on_modified(event):
    """Called when a file or directory is modified.
     :param event:
         Event representing file/directory modification.
     """
    print(f"on_modified: {event.src_path}")


def on_moved(event):
    """Called when a file or a directory is moved or renamed.
    :param event:
        Event representing file/directory movement.
    """
    print(f"on_moved: from {event.src_path} to {event.dest_path}")


def on_closed(event):
    """Called when a file opened for writing is closed.
    :param event:
        Event representing file closing.
    """
    print(f"on_closed: {event.src_path}")


# def on_any_event(event):
#     print(f"on_any_event:{event.src_path}")


def get_random_string(length):
    """
    :param length: is the string length.
    :return: The function creates a string that contain digits or english lower and upper case letters.
    """
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for i in range(length))


def send_file_data(socket, file_name, abs_file_path, start):
    """
    sent the file's data.
    :param socket: for send.
    :param file_name: the file name.
    :param abs_file_path: the absolute path of file's parent.
    :param start: for sending the relative path of the files and its data.
    """
    # send the relative file's path.
    socket.send(os.path.join(os.path.relpath(abs_file_path, start), file_name).encode(FORMAT))
    socket.recv(SIZE).decode(FORMAT)
    # open the file and read data
    new_file = open(os.path.join(abs_file_path, file_name), 'rb')
    data = new_file.read(SIZE)
    # send all file's data.
    while data:
        socket.send(data)
        socket.recv(SIZE)
        data = new_file.read(SIZE)
    # finish sending this file
    socket.send(END_ONE_FILE)
    socket.recv(SIZE).decode(FORMAT)
    new_file.close()


def send_all(socket, source_dir_path, start):
    """
    send from source_dir_path the directory with all its files and directories.
    :param socket: for send.
    :param source_dir_path: the absolute path of dir we want to send.
    :param start: for sending the relative path of the files and directories.
    """
    # loop runs on all files and directories from source_dir_path recursively (top to down).
    for dir_path, dirs_list, files_list in os.walk(source_dir_path, topdown=True):
        # send the dir_path.
        socket.send(dir_path.encode(FORMAT))
        socket.recv(SIZE)
        # sending all the dirs names.
        for dir_name in dirs_list:
            socket.send(os.path.join(os.path.relpath(dir_path, start), dir_name).encode(FORMAT))
            socket.recv(SIZE).decode(FORMAT)
        # finished with sending the dirs and starting with sending the files.
        socket.send(END_DIRS.encode(FORMAT))
        socket.recv(SIZE).decode(FORMAT)
        for file_name in files_list:
            send_file_data(socket, file_name, dir_path, start)
        # finished with sending all files.
        socket.send(END_FILES.encode(FORMAT))
        socket.recv(SIZE)
    # finished with sending all.
    socket.send(END_SEND_ALL)


def receive_dirs_from_path(socket, des_folder_path):
    """
    for receiving dirs and put them in destination folder path
    :param socket:  received from
    :param des_folder_path: destination path for given directories
    """
    # received dir's name
    dir_name = bytes(socket.recv(SIZE)).decode(FORMAT)
    socket.send(b'dir_name received')
    # loop runs until received all the dirs.
    while not dir_name == END_DIRS:
        dir_path = os.path.join(des_folder_path, dir_name)
        os.makedirs(dir_path)
        dir_name = bytes(socket.recv(SIZE)).decode(FORMAT)
        socket.send(b'dir_name received')


def receive_files_from_path(socket, des_folder_path):
    """
    for receiving files and put them in destination folder path
    :param socket:  received from
    :param des_folder_path: destination path for given files
    """
    # received file's name
    file_name = bytes(socket.recv(SIZE)).decode(FORMAT)
    socket.send(b'file_name received')
    # loop runs until received all the files.
    while not file_name == END_FILES:
        # creates the file
        file_path = os.path.join(des_folder_path, file_name)
        with open(file_path, 'wb') as f:
            file_data = socket.recv(SIZE)
            socket.send(b'file_data received')
            # write in file
            while not file_data == END_ONE_FILE:
                f.write(file_data)
                file_data = socket.recv(SIZE)
                socket.send(b'file_data received')
        # after create and write the file
        f.close()
        file_name = bytes(socket.recv(SIZE)).decode(FORMAT)
        socket.send(b'file_name received')


def receive_all(socket, des_folder_path):
    """
    recieve from socket directory with all its files and directories
    and puts them in des_folder_path
    :param socket: received from
    :param des_folder_path: destination path for the received files and directories.
    """
    # receive the main dir
    dir = bytes(socket.recv(SIZE)).decode(FORMAT)
    socket.send(b' dir received')
    dir_path = os.path.join(des_folder_path, os.path.basename(dir))
    # creates the dir of the dir_path
    os.makedirs(dir_path)
    # loop runs until it got all the directories and files of the main dir.
    while not dir == END_SEND_ALL.decode(FORMAT):
        # receive all the folders in dir
        receive_dirs_from_path(socket, des_folder_path)
        # receive all the files in dir
        receive_files_from_path(socket, des_folder_path)
        # get the next dir.
        dir = bytes(socket.recv(SIZE)).decode(FORMAT)
        socket.send(b' dir received')
