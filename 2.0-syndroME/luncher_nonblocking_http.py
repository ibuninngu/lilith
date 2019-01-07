import sl_sockets.non_blocking as SOCKET
import sl_server.http.http as HANDLER
import socket

listen = 128
bind_ip = "localhost"
bind_port=80
timeout = 60

print("[*]bindIP: %s  bindPORT: %d\n[?]Socket:NON-BLOCKING MODE" % (bind_ip, bind_port))
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setblocking(False)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
server_sock.bind((bind_ip, bind_port))
server_sock.listen(listen)

HANDLER.root_dir = "./sl_contents/example.com/http/www"
HANDLER.message_dir = "./sl_contents/example.com/http/messages"
SOCKET.SERVER = HANDLER
SOCKET.main(server_sock, timeout)
