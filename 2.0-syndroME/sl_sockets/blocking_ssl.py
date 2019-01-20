import threading
import socket

LOCK = threading.Lock()
timeout = 30.0
SERVER = None
SSL_CONTEXT = None

def accept_thread(server_sock):
    while(True):
        LOCK.acquire()
        new_sock, addr = server_sock.accept()
        connstream = SSL_CONTEXT.wrap_socket(new_sock, server_side=True)
        LOCK.release()
        connstream.settimeout(timeout)
        message = SERVER.main(connstream)
        connstream.send(message)
        connstream.close()

def main(listening_socket, thread_range):
    thread_list = []
    for _ in range(thread_range):
        thread = threading.Thread(target=accept_thread, args=(listening_socket,))
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()