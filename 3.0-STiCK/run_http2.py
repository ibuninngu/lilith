import servers.http2.http2 as SERVER

import socket

SERVER.BIND_IP = socket.gethostbyname(socket.gethostname())

print("HTTP2",SERVER.BIND_IP,":",SERVER.BIND_PORT)
SERVER.start()