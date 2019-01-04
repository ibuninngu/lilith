# -*- coding: utf-8 -*-

import socket

#log file format
#CSV
#datetime, thread_name, loglevel, filename, filelineno, message

thread_range = 40

bind_ip = socket.gethostbyname(socket.gethostname())
bind_port = 80
bind_port_ssl = 443
listen = 128
recv_val = 4096
server_name = "DiCE-Lilith/1.0"
server_root = "./contents/example.com"
certfile="./Encript/example.com/cert1.pem"
keyfile="./Encript/example.com/privkey1.pem"
log_file="log.conf"
