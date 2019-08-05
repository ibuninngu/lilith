import servers.smtp.smtp_auth as SERVER

import socket

SERVER.my_domain = b"example.com"
SERVER.BIND_IP = socket.gethostbyname(socket.gethostname())

print("SMTP-AUTH",SERVER.BIND_IP,":",SERVER.BIND_PORT)
SERVER.start()