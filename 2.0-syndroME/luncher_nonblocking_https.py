import pl_sockets.non_blocking_ssl as SOCKET
import pl_server.http.lilith_http as HANDLER
import socket
import ssl

listen = 128
bind_ip = "localhost"
bind_port=80
bind_port_ssl = 443
timeout = 60
certfile="./sl_contents/Encript/example.com/cert.pem"
keyfile="./sl_contents/Encript/example.com/privkey.pem"

print("[*]bindIP: %s  bindPORT: %d\n[?]Socket:NON-BLOCKING MODE" % (bind_ip, bind_port_ssl))

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=certfile, keyfile=keyfile)
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setblocking(False)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
server_sock.bind((bind_ip, bind_port_ssl))
server_sock.listen(listen)

HANDLER.root_dir = "./sl_contents/example.com/http/www"
HANDLER.message_dir = "./sl_contents/example.com/http/messages"
SOCKET.SERVER = HANDLER
SOCKET.SSL_CONTEXT = context
SOCKET.main(server_sock, timeout)
