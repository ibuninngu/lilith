import select

read_waiters = {}
write_waiters = {}
connections = {}

timeout = 30.0
SERVER = None

def accept_handler(serversocket):
    clientsocket, (client_address, client_port) = serversocket.accept()
    clientsocket.setblocking(False)
    clientsocket.settimeout(timeout)
    connections[clientsocket.fileno()] = (clientsocket, client_address, client_port)
    read_waiters[clientsocket.fileno()] = (recv_handler, (clientsocket.fileno(), ))
    read_waiters[serversocket.fileno()] = (accept_handler, (serversocket, ))

def recv_handler(fileno):
    def terminate():
        del connections[clientsocket.fileno()]
        clientsocket.close()
        print("SOCKET CLOSED")
    try:
        clientsocket, client_address, client_port = connections[fileno]
        message = SERVER.main(clientsocket)
        write_waiters[fileno] = (send_handler, (fileno, message))
    except OSError:
        terminate()
        return

def send_handler(fileno, message):
    def terminate():
        del connections[clientsocket.fileno()]
        clientsocket.close()
        print("SOCKET CLOSED")
    try:
        clientsocket, client_address, client_port = connections[fileno]
        sent_len = clientsocket.send(message)
        if sent_len == len(message):
            read_waiters[clientsocket.fileno()] = (recv_handler,(clientsocket.fileno(), ))
        else:
            write_waiters[fileno] = (send_handler,(fileno, message[sent_len:]))
    except OSError:
        terminate()
        return
        
def main(listening_socket, timeout):
    read_waiters[listening_socket.fileno()] = (accept_handler, (listening_socket, ))
    while True:
        rlist, wlist, _ = select.select(read_waiters.keys(), write_waiters.keys(), [], timeout)
        for r_fileno in rlist:
            handler, args = read_waiters.pop(r_fileno)
            handler(*args)
        for w_fileno in wlist:
            handler, args = write_waiters.pop(w_fileno)
            handler(*args)