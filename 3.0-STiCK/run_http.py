import servers.http.http as SERVER
import socket

# Enable SSL
#SERVER.SSL = True
#SERVER.BIND_PORT = 443

SERVER.BIND_IP = socket.gethostbyname(socket.gethostname())
print("HTTP",SERVER.BIND_IP,":",SERVER.BIND_PORT)
SERVER.start()