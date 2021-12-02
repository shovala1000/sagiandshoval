import os
import string
import random
import watchdog
from watchdog.events import PatternMatchingEventHandler, FileSystemEventHandler

FORMAT = 'utf-8'
SIZE = 1024
CLIENT_NOT_RECOGNIZED = 'no recognize'
CLIENT_HAS_NO_INDEX = '-1'
BYTES_FOR_INDEX = 4
END_DIRS = 'End dirs'
END_FILES = 'End files'
END_ONE_FILE = b'End one file'
END_SEND_ALL = b'end_send_all'


class MonitorFolder(FileSystemEventHandler):
    def __init__(self, recognizer, event_queue):
        # self.s = des_socket
        self.r = recognizer
        self.event_queue = event_queue

    def get_queue(self):
        return self.event_queue

    def on_created(self, event):
        """Called when a file or directory is created.
        :param event:
            Event representing file/directory creation.
        """
        print(f"on_created: {event.src_path}")
        self.event_queue.put(event)

    def on_deleted(self, event):
        """Called when a file or directory is deleted.
         :param event:
             Event representing file/directory deletion.
         """
        print(f"on_deleted: {event.src_path}")
        self.event_queue.put(event)

    def on_modified(self, event):
        """Called when a file or directory is modified.
         :param event:
             Event representing file/directory modification.
         """
        print(f"on_modified: {event.src_path}")
        # self.event_queue.put(event)

    def on_moved(self, event):
        """Called when a file or a directory is moved or renamed.
        :param event:
            Event representing file/directory movement.
        """
        print(f"on_moved: from {event.src_path} to {event.dest_path}")
        self.event_queue.put(event)

    def on_closed(self, event):
        """Called when a file opened for writing is closed.
        :param event:
            Event representing file closing.
        """
        print(f"on_closed: {event.src_path}")
        self.event_queue.put(event)

    # def set_socket(self, des_socket):
    #     self.s = des_socket


def get_random_string(length):
    """
    :param length: is the string length.
    :return: The function creates a string that contain digits or english lower and upper case letters.
    """
    return ''.join(
        random.choice(string.ascii_lowercase + string.digits + string.ascii_uppercase) for i in range(length))


def send_file_data(s, file_name, abs_file_path, start=None):
    """
    sent the file's data.
    :param s: for send.
    :param file_name: the file name.
    :param abs_file_path: the absolute path of file's parent.
    :param start: for sending the relative path of the files and its data.
    """
    # send the relative file's path.
    s.send(os.path.join(os.path.relpath(abs_file_path, start), file_name).encode(FORMAT))
    s.recv(SIZE).decode(FORMAT)
    # open the file and read data
    new_file = open(os.path.join(abs_file_path, file_name), 'rb')
    data = new_file.read(SIZE)
    # send all file's data.
    while data:
        s.send(data)
        s.recv(SIZE)
        data = new_file.read(SIZE)
    # finish sending this file
    s.send(END_ONE_FILE)
    s.recv(SIZE).decode(FORMAT)
    new_file.close()


def send_all(s, source_dir_path, start):
    """
    send from source_dir_path the directory with all its files and directories.
    :param s: for send.
    :param source_dir_path: the absolute path of dir we want to send.
    :param start: for sending the relative path of the files and directories.
    """
    # loop runs on all files and directories from source_dir_path recursively (top to down).
    for dir_path, dirs_list, files_list in os.walk(source_dir_path, topdown=True):
        # send the dir_path.
        s.send(dir_path.encode(FORMAT))
        s.recv(SIZE)
        # sending all the dirs names.
        for dir_name in dirs_list:
            s.send(os.path.join(os.path.relpath(dir_path, start), dir_name).encode(FORMAT))
            s.recv(SIZE).decode(FORMAT)
        # finished with sending the dirs and starting with sending the files.
        s.send(END_DIRS.encode(FORMAT))
        s.recv(SIZE).decode(FORMAT)
        for file_name in files_list:
            send_file_data(s, file_name, dir_path, start)
        # finished with sending all files.
        s.send(END_FILES.encode(FORMAT))
        s.recv(SIZE)
    # finished with sending all.
    s.send(END_SEND_ALL)


def receive_dirs_from_path(s, des_folder_path):
    """
    for receiving dirs and put them in destination folder path
    :param s:  received from
    :param des_folder_path: destination path for given directories
    """
    # received name of dir.
    dir_name = bytes(s.recv(SIZE)).decode(FORMAT)
    s.send(b'dir_name received')
    # loop runs until received all the dirs.
    while not dir_name == END_DIRS:
        dir_path = os.path.join(des_folder_path, dir_name)
        os.makedirs(dir_path)
        dir_name = bytes(s.recv(SIZE)).decode(FORMAT)
        s.send(b'dir_name received')


def receive_files_from_path(s, des_folder_path):
    """
    for receiving files and put them in destination folder path
    :param s:  received from
    :param des_folder_path: destination path for given files
    """
    # received file's name
    file_name = bytes(s.recv(SIZE)).decode(FORMAT)
    s.send(b'file_name received')
    # loop runs until received all the files.
    while not file_name == END_FILES:
        # creates the file
        file_path = os.path.join(des_folder_path, file_name)
        with open(file_path, 'wb') as f:
            file_data = s.recv(SIZE)
            s.send(b'file_data received')
            # write in file
            while not file_data == END_ONE_FILE:
                f.write(file_data)
                file_data = s.recv(SIZE)
                s.send(b'file_data received')
        # after create and write the file
        f.close()
        file_name = bytes(s.recv(SIZE)).decode(FORMAT)
        s.send(b'file_name received')


def receive_all(s, des_folder_path):
    """
    receive from socket directory with all its files and directories
    and puts them in des_folder_path
    :param s: received from
    :param des_folder_path: destination path for the received files and directories.
    """
    # receive the main dir
    current_dir = bytes(s.recv(SIZE)).decode(FORMAT)
    s.send(b' dir received')
    dir_path = os.path.join(des_folder_path, os.path.basename(current_dir))
    # creates the dir of the dir_path
    os.makedirs(dir_path)
    # loop runs until it got all the directories and files of the main dir.
    while not current_dir == END_SEND_ALL.decode(FORMAT):
        # receive all the folders in dir
        receive_dirs_from_path(s, des_folder_path)
        # receive all the files in dir
        receive_files_from_path(s, des_folder_path)
        # get the next dir.
        current_dir = bytes(s.recv(SIZE)).decode(FORMAT)
        s.send(b' dir received')


def send_changes(event_queue, s):
    """
    send from socket all the events from event_queue
    :param event_queue: is EventQueue
    :param s: is a socket to send from
    """
    print("in send_changes")
    print("event_queue: "+str(event_queue.queue))
    while not event_queue.empty():
        current_event = event_queue.get()
        # get type, path and if is directory information.
        if watchdog.events.EVENT_TYPE_MOVED == current_event.event_type:
            event_type, src_path, dest_path, is_directory = current_event.key
        else:
            dest_path = ''
            event_type, src_path, is_directory = current_event.key
        # send event type
        s.send(event_type.encode(FORMAT))
        print("send event type: "+event_type)
        s.recv(SIZE)
        # send event src_path
        s.send(src_path.encode(FORMAT))
        s.recv(SIZE)
        if watchdog.events.EVENT_TYPE_MOVED == event_type:
            # send event dest_path
            s.send(dest_path.encode(FORMAT))
            s.recv(SIZE)
        # send if is directory
        s.send(str(is_directory).encode(FORMAT))
        s.recv(SIZE)
        if watchdog.events.EVENT_TYPE_MOVED == event_type:
            if not is_directory:
                send_file_data(s, os.path.basename(dest_path), os.path.abspath(os.path.join(dest_path, os.pardir)))
                # finished with sending all files.
                s.send(END_FILES.encode(FORMAT))
                s.recv(SIZE)
        if watchdog.events.EVENT_TYPE_CREATED == event_type:
            if not is_directory:
                send_file_data(s, os.path.basename(src_path), os.path.abspath(os.path.join(src_path, os.pardir)))
                # finished with sending all files.
                s.send(END_FILES.encode(FORMAT))
                s.recv(SIZE)
    s.send(b'End')
    s.recv(SIZE)


def receive_changes(s):
    print("in receive")
    # receive event type
    event_type = s.recv(SIZE).decode(FORMAT)
    s.send(b'type received')
    while not "End" == event_type:
        # receive event src_path
        src_path = s.recv(SIZE).decode(FORMAT)
        s.send(b'src_path received')
        dest_path = ""
        # receive dest_type
        if watchdog.events.EVENT_TYPE_MOVED == event_type:
            dest_path = s.recv(SIZE).decode(FORMAT)
            s.send(b'dest_path received')
        # receive if is directory
        is_directory = s.recv(SIZE).decode(FORMAT)
        s.send(b'is_directory received')
        # receive event according to the type protocol
        print("go to protocol: "+event_type)
        if watchdog.events.EVENT_TYPE_CREATED == event_type:
            on_created_protocol(is_directory, src_path, s)
        elif watchdog.events.EVENT_TYPE_DELETED == event_type:
            on_deleted_protocol(is_directory, src_path)
        elif watchdog.events.EVENT_TYPE_MOVED == event_type:
            on_moved_protocol(is_directory, src_path, dest_path, s)
        elif watchdog.events.EVENT_TYPE_CLOSED == event_type:
            on_closed_protocol()
        # receive event type
        event_type = s.recv(SIZE).decode(FORMAT)
        s.send(b'type received')


def on_created_protocol(is_directory, src_path, s):
    print("in created")
    current_path = "/home/shoval/PycharmProjects/sagiandshoval/test2"
    path = os.path.join(current_path, os.path.relpath(src_path))
    if 'True' == is_directory:
        os.makedirs(path)
    else:
        print("need to create a file")
        receive_files_from_path(s, current_path)


def on_deleted_protocol(is_directory, src_path):
    path = os.path.join("/home/shoval/PycharmProjects/sagiandshoval/test2", os.path.relpath(src_path))
    if 'True' == is_directory:
        os.rmdir(path)
    else:
        os.remove(path)


def on_moved_protocol(is_directory, src_path, dest_path, s):
    on_created_protocol(is_directory, dest_path, s)
    on_deleted_protocol(is_directory, src_path)


def on_closed_protocol():
    print("in close")
