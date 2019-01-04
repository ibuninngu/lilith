import socket
import ssl
import sl_server.http2.http2 as http2

bind_ip = socket.gethostbyname(socket.gethostname())
bind_port_ssl = 443

certfile="./sl_contents/Encript/example.com/cert.pem"
keyfile="./sl_contents/Encript/example.com/privkey.pem"
listen = 128

# server_sock
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setblocking(False)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
server_sock.bind((bind_ip, bind_port_ssl))
server_sock.listen(listen)

print(bind_ip, ":",bind_port_ssl)
print("http2-NonBlockingMode")
http2.cert_file = certfile
http2.key_file = keyfile
http2.root_directory="./sl_contents/example.com/http/www"
http2.message_directory="./sl_contents/example.com/http/message"
http2.main(server_sock)
