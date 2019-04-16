import post_action_list_auto_gen as auto_gen
auto_gen.auto_gen()

import sl_server.http.http as HANDLER
import sl_sockets.blocking as SOCKET
import socket

thread_range = 40
listen = 128
#bind_ip = "localhost"
bind_ip = socket.gethostbyname(socket.gethostname())
bind_port=80

print("[*]bindIP: %s  bindPORT: %d\n[?]Socket:BLOCKING MODE" % (bind_ip, bind_port))    
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind((bind_ip, bind_port))
server_sock.listen(listen)

HANDLER.root_dir = "./sl_contents/example.com/http/www"
HANDLER.message_dir = "./sl_contents/example.com/http/messages"
SOCKET.SERVER = HANDLER
SOCKET.main(server_sock, thread_range)
