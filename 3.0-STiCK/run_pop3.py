import servers.pop3.pop3 as SERVER

import socket

SERVER.BIND_IP = socket.gethostbyname(socket.gethostname())

print("POP3",SERVER.BIND_IP,":",SERVER.BIND_PORT)
SERVER.start()