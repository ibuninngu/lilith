import threading
import socket

LOCK = threading.Lock()
timeout = 30.0
SERVER = None

def accept_thread(server_sock):
    while(True):
        LOCK.acquire()
        new_sock, addr = server_sock.accept()
        LOCK.release()
        new_sock.settimeout(timeout)
        SERVER.SOCKET = new_sock
        message = SERVER.main(new_sock)
        SERVER.SOCKET.send(message)
        new_sock.close()

def main(listening_socket, thread_range):
    thread_list = []
    for _ in range(thread_range):
        thread = threading.Thread(target=accept_thread, args=(listening_socket,))
        thread.start()
        thread_list.append(thread)
    for thread in thread_list:
        thread.join()