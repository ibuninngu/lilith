# -*- coding: utf-8 -*-

import logging
from logging import config
import ssl
import socket
import threading
import sys
import lilith_defines
import Lilith_action.get
import Lilith_action.post
reload(sys)
sys.setdefaultencoding("utf-8")

print("[*]bindIP: %s  bindPORT: %d\n" % (lilith_defines.bind_ip, lilith_defines.bind_port_ssl))
config.fileConfig(fname=lilith_defines.log_file, disable_existing_loggers=False)

def make_http_header(status="200 OK", server="Server", Accept_Ranges="bytes", Content_Length="0", Keep_Alive="timeout=15, max=100", Content_Type="media/binary"):
    return("HTTP/1.1 " + status + \
           "\r\nServer: " + server + \
           "\r\nAccept-Ranges: " + Accept_Ranges + \
           "\r\nContent-Length: " + Content_Length + \
           "\r\nKeep-Alive: " + Keep_Alive + \
           "\r\nContent-Type: " + Content_Type + \
           "\r\n\r\n")

def handler(socket):
    socket.settimeout(30.0)
    while(True):
        message = ""
        try:
            request = str(socket.recv(lilith_defines.recv_val))
        except:
            socket.close()
            return
        if(len(request) == 0):
            socket.close()
            return
        method = request.split("\r\n")[0].split(" ")
        if method[0] == "GET":
            if(-1 == request.split("\r\n")[0].split(" ")[1].find("?")):
                content, content_type, g_status = get.get(request, lilith_defines.server_root)
                message = make_http_header(status=g_status, server=lilith_defines.server_name, Content_Length=str(len(content)), Content_Type=content_type) + content
            else:
                R = request.split("\r\n")[0].split(" ")[1].split("?")[0]
                content, content_type, p_status = Lilith_action.post.post("POST "+R+" HTTP/1.1\r\n\r\n"+request.split("\r\n")[0].split(" ")[1])
                message = make_http_header(status=p_status, server=lilith_defines.server_name, Content_Length=str(len(content)), Content_Type=content_type) + content
        elif method[0] == "POST":
            content, content_type, p_status = Lilith_action.post.post(request)
            message = make_http_header(status=p_status,server=lilith_defines.server_name, Content_Length=str(len(content)), Content_Type=content_type) + content
        elif method[0] == "BOST":
            while True:
                if(request[-5:] == "[END]"):
                    break
                try:
                    data = str(socket.recv(lilith_defines.recv_val))
                except:
                    socket.close()
                    return
                request += data
            content, content_type, p_status = Lilith_action.post.post(request[:-5])
            message = make_http_header(status=p_status,server=lilith_defines.server_name, Content_Length=str(len(content)), Content_Type=content_type) + content
        socket.send(message)


SERVER_ROOT = lilith_defines.server_root
POST_LIST = Lilith_action.post.action_list.post_list
SERVER_RUN = True

def maintenance_mode(FLG):
    if(FLG):
        logging.info("StartMaintenanceMode")
        lilith_defines.server_root = "./coontents_maintenance/example.com"
        Lilith_action.post.action_list.post_list = {}
    else:
        logging.info("ExitMaintenanceMode")
        lilith_defines.server_root = SERVER_ROOT
        Lilith_action.post.action_list.post_list = POST_LIST

def server_loop():
    logging.info("ServerRun")
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=lilith_defines.certfile, keyfile=lilith_defines.keyfile)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((lilith_defines.bind_ip, lilith_defines.bind_port_ssl))
    server.listen(lilith_defines.listen)    
    while SERVER_RUN:
        try:
            (client, addr) = server.accept()
            connstream = context.wrap_socket(client, server_side=True)
            client_handler = threading.Thread(target=handler, args=(connstream,), name=str(addr[0]))
            client_handler.start()
        except:
            pass
    logging.info("ServerStop")

def main():
    SERVER_LOOP = threading.Thread(target=server_loop, name=str("DiCE-Lilith-MainThread"))
    SERVER_LOOP.start()