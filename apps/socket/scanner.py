import threading
import time
from queue import Queue
from socket import AF_INET, SOCK_STREAM, gethostbyname, socket

queue = Queue()

ip_to_scan = input('Enter the host to be scanned: ')

def scan(port):
    host_ip = gethostbyname(ip_to_scan)
    print('Starting scan on host: ', host_ip)

    try:
        s = socket(AF_INET, SOCK_STREAM)
    except:
        pass
    else:
        print('Connecting...')
        connection = s.connect_ex((host_ip, port))
        if connection == 0:
            print(f'Port {i}: OPEN')
        s.close()


def start_thread():
    while True:
        port = queue.get()
        print('Scan started for port %s' % port)
        scan(port)
        queue.task_done()


def create_threads(n_threads=5):
    for _ in range(1, n_threads):
        thread = threading.Thread(target=start_thread)
        thread.start()
    threading.enumerate()


def init_queue():
    for i in range(50, 60):
        queue.put(i)
    create_threads()

queue.join()

init_queue()
