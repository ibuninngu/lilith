# Lilith HTTP server

import sl_functions.http.get as get
import sl_functions.http.post as post
import sl_functions.http.gept as gept
import sl_functions.http.make_http_header as make_http_header

# ========== DEFINES ========== #
recv_val = 4096
#1024...1kb **2...1Mb
buf_limit = 1024 ** 2
buf_limit_int = int(buf_limit / recv_val)
message = ""
messages_dir="./sl_contents/http/messages"

# Need for blocking socket...
SOCKET = None

def GET(request, header_params, body):
    if(request[1].find("?") != -1):
        pfg = request[1].split("?")
        content, content_type, p_status = gept.gept(pfg[0], pfg[1])
        return make_http_header.make_http_header(status=p_status, Content_Length=str(len(content)), Content_Type=content_type), content.encode("utf-8")
    content, content_type, g_status = get.get(request[1])
    return make_http_header.make_http_header(status=g_status, Content_Length=str(len(content)), Content_Type=content_type), content

def POST(request, header_params, body):
    content, content_type, p_status = post.post(request[1], body)
    return make_http_header.make_http_header(status=p_status, Content_Length=str(len(content)), Content_Type=content_type), content

def main(socket):
    def SEND():
        send_len = socket.send(message.encode("utf-8"))
        if send_len == len(message):
            return True
        else:
            return False
    total_buf_int = 0
    header_params = {}
    body = ""
    tmp_buf = socket.recv(recv_val)
    buf = tmp_buf.decode("utf-8")
    request = buf[0:buf.find("\r\n")].split(" ")
    print(len(tmp_buf))
    print(tmp_buf)
    #recv all headers
    for _ in range(buf_limit_int):
        point_body_buf = buf.find("\r\n\r\n")
        if(point_body_buf != -1):
            break            
        tmp_buf = socket.recv(recv_val).decode("utf-8")
        buf += tmp_buf
    header = buf.split("\r\n")
    #http headers to hash-map
    for param in header[1:-2]:
        p = param.split(": ")
        header_params.update({p[0]:p[1]})
    if(request[0] == "GET"):
        h, get_buf = GET(request, header_params, body)
        message = h.encode("utf-8") + get_buf
        return message
    elif(request[0] == "POST"):
        # recv message body
        content_length = int(header_params["Content-Length"])
        # first, check Content_Length from header
        if(buf_limit < content_length):
            content, content_type, g_status = get.get("/413.html", direc=messages_dir)
            message = make_http_header.make_http_header(status=413, Content_Length=str(len(content)), Content_Type=content_type)
            return message.encode("utf-8")+content
        # recv while Content_Length
        body = buf[point_body_buf+4:]
        body_len_int = -(-(content_length - len(body)) // recv_val)
        for _ in range(body_len_int):
            tmp_buf = socket.recv(recv_val).decode("utf-8")
            body += tmp_buf
        h, post_buf = POST(request, header_params, body)
        message = (h + post_buf).encode("utf-8")
        return message
    else:
        get_buf, content_type, g_status = get.get("/501.html", direc=messages_dir)
        message = make_http_header.make_http_header(status=501, Content_Length=str(len(get_buf)), Content_Type=content_type)
        return message.encode("utf-8")+content