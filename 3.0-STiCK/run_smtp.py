import servers.smtp.smtp as SERVER

import socket

SERVER.my_domain = b"example.com"
SERVER.BIND_IP = socket.gethostbyname(socket.gethostname())

print("SMTP",SERVER.BIND_IP,":",SERVER.BIND_PORT)
SERVER.start()