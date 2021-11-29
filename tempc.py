from utils import *

# RECOGNIZE = "rhD5EtKGBkMmCewufNLnttdlwJlsgWRsw3zJbcqKxBzfnH1hy3SDIb5HRIYTCw25RNXVtJwD2BiKsOuAbRqwoRbdCqpQZrKltrLudDuAdUlhQMZWh6mFgGzRAnJw6LMI"

RECOGNIZE = CLIENT_NOT_RECOGNIZED
SERVER_IP = "127.0.0.1"
SERVER_PORT = "12346"
DIR_FOLDER = "/home/shoval/PycharmProjects/sagiandshoval/test"  # sys.argv[3]
TIME = "10"


def init_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, int(SERVER_PORT)))
    s.send(DIR_FOLDER.encode(FORMAT))
    s.recv(SIZE)
    return s


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_event_queue = EventQueue()
my_handler = MonitorFolder(s, RECOGNIZE, my_event_queue)
my_event_queue = EventQueue()

my_observer = Observer()
my_observer.schedule(my_handler, "/home/shoval/PycharmProjects/sagiandshoval/test", True)

my_observer.start()

try:
    while True:
        # print queue
        print("hendler_queue: " + str(my_handler.get_queue().queue))
        time.sleep(int(TIME))
        # s.send("")
except KeyboardInterrupt:
    my_observer.stop()
my_observer.join()
