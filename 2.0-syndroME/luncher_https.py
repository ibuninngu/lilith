import sl_server.http.http as HANDLER
import sl_sockets.blocking_ssl as SOCKET
import socket
import ssl

thread_range = 40
listen = 128
bind_ip = "localhost"
bind_port_ssl = 443
certfile="./sl_contents/Encript/example.com/cert.pem"
keyfile="./sl_contents/Encript/example.com/privkey.pem"

print("[*]bindIP: %s  bindPORT: %d\n[?]Socket:BLOCKING MODE" % (bind_ip, bind_port_ssl))    
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=certfile, keyfile=keyfile)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind((bind_ip, bind_port_ssl))
server_sock.listen(listen)

HANDLER.root_dir = "./sl_contents/example.com/http/www"
HANDLER.message_dir = "./sl_contents/example.com/http/messages"
SOCKET.SERVER = HANDLER
SOCKET.SSL_CONTEXT = context
SOCKET.main(server_sock, thread_range)
