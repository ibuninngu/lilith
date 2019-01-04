# -*- coding: utf-8 -*-

import socket
import threading
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
print ('defaultencoding:', sys.getdefaultencoding())

bind_ip = "localhost"
bind_port = 80

print("bindIP: %s  bindPORT: %d\n" % (bind_ip, bind_port))

def post_test(params):
    params = params[-1].split("&")
    buf = ""
    for line in params:
        buf += "<p>" + line + "</p>"
    return(buf, "text/html")

def make_http_header(status="200 OK", server="Server", Accept_Ranges="bytes", Content_Length="0", Keep_Alive="timeout=15, max=100", Content_Type="media/binary"):
    return("HTTP/1.1 " + status + \
           "\r\nServer: " + server + \
           "\r\nAccept-Ranges: " + Accept_Ranges + \
           "\r\nContent-Length: " + Content_Length + \
           "\r\nKeep-Alive: " + Keep_Alive + \
           "\r\nContent-Type: " + Content_Type + \
           "\r\n\r\n")

def content_det(s):
    return(media_list[s.split(".")[1]] + "/" + s.split(".")[1])

def GET(req):
    req = req[0].split(" ")[1].replace("../", "")
    try:
        if req != "/":
            f = open("contents" + req, "rb")
            buf = f.read()
            f.close()
        else:
            req = "/index.html"
            f = open("contents" + req, "rb")
            buf = f.read()
            f.close()
        print("____GET---> contents" + req + " OK\n")
        return(buf, content_det(req))
    except:
        print("____OPEN FAILED---> contents" + req + "\n")
        return("<h1>Status 404</h1><br><p>" + req + " is NOT FOUND</p>", "text/html")

def POST(req):
    try:
        content, content_type = post_list[req[0].split(" ")[1].split("/")[-1]](req)
        print("____POST---> " + req[0].split(" ")[1].split("/")[-1] + " ::: " + req[-1] +  " OK\n")
        return(content, content_type)
    except:
        print("____POST FAILED---> "  + req[0].split(" ")[1].split("/")[-1] + " ::: " + req[-1] + "\n")
        return("<h1>Status 400</h1><br><p>THERE'S A BAD MOON ON THE RISE</p>", "text/html")

def handler(socket):
    request = socket.recv(4096).split("\r\n")
    method = request[0].split(" ")
    message = ""
    try:
        print ("request: %s :: from: %s\n" % (request[0], request[1][6:]))
    except:
        pass
    if method[0] == "GET":
        content, content_type = GET(request)
        message = make_http_header(server="SCETCH-Lilith/0.0", Content_Length=str(len(content)), Content_Type=content_type) + content
    elif method[0] == "POST":
        content, content_type = POST(request)
        message = make_http_header(server="SCETCH-Lilith/0.0", Content_Length=str(len(content)), Content_Type=content_type) + content
    socket.send(message)
    socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(24)
    while True:
        (client, addr) = server.accept()
        client_handler = threading.Thread(target=handler, args=(client,))
        client_handler.start()

media_list = {
    "html":"text",
    "txt":"text",
    "css":"text",
    "js":"text",
    "jpg":"image",
    "png":"image",
    "ico":"image",
    "mp4":"video",
    "mp3":"audio"
    }
    
post_list = {
    "test.post":post_test
    }

main()
