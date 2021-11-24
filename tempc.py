
from utils import *

# RECOGNIZE = "rhD5EtKGBkMmCewufNLnttdlwJlsgWRsw3zJbcqKxBzfnH1hy3SDIb5HRIYTCw25RNXVtJwD2BiKsOuAbRqwoRbdCqpQZrKltrLudDuAdUlhQMZWh6mFgGzRAnJw6LMI"

RECOGNIZE = CLIENT_NOT_RECOGNIZED
SERVER_IP = "127.0.0.1"
SERVER_PORT = "12346"
DIR_FOLDER = "/home/shoval/PycharmProjects/sagiandshoval/test"  # sys.argv[3]
TIME = "10"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, int(SERVER_PORT)))
s.send(DIR_FOLDER.encode(FORMAT))
s.recv(SIZE)

patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved
my_event_handler.on_closed = on_closed
# my_event_handler.on_any_event = on_any_event



my_observer = Observer()
my_observer.schedule(my_event_handler, DIR_FOLDER, recursive=True)
# my_observer = EventEmitter(my_observer.event_queue,my_event_handler)
# my_observer_queue = my_observer.
my_observer.start()
try:
    while True:
        # print queue
        time.sleep(int(TIME))
except KeyboardInterrupt:
    my_observer.stop()
my_observer.join()
