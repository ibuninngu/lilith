import sl_sockets.blocking as blocking
import socket

import sl_server.http.lilith_http as HANDLER

thread_range = 40
listen = 128
bind_ip = "127.0.0.1"
bind_port=80

print("[*]bindIP: %s  bindPORT: %d\n[?]Socket:BLOCKING MODE" % (bind_ip, bind_port))    
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((bind_ip, bind_port))
server_sock.listen(listen)

blocking.SERVER = HANDLER
blocking.main(server_sock, thread_range)
